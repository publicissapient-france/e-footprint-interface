from typing import List

import pandas as pd
import numpy as np
from efootprint.abstract_modeling_classes.explainable_objects import ExplainableQuantity, EmptyExplainableObject, \
    ExplainableHourlyQuantities
from efootprint.abstract_modeling_classes.source_objects import SourceValue, SourceObject, SourceHourlyValues
from efootprint.core.country import Country
from efootprint.core.usage.usage_journey import UsageJourney
from efootprint.core.usage.usage_pattern import UsagePattern
from efootprint.core.hardware.device import Device
from efootprint.core.hardware.network import Network
from efootprint.constants.units import u
from efootprint.utils.tools import time_it


class UsagePatternFromForm(UsagePattern):
    @classmethod
    def list_values(cls):
        return {
            "initial_usage_journey_volume_timespan": [SourceObject("monthly"), SourceObject("yearly")],
            "net_growth_rate_timespan": [SourceObject("monthly"), SourceObject("yearly")]
        }

    def __init__(self, name: str, usage_journey: UsageJourney, devices: List[Device],
                 network: Network, country: Country, start_date: SourceObject, modeling_duration: SourceValue,
                 initial_usage_journey_volume: SourceValue, initial_usage_journey_volume_timespan: SourceObject,
                 net_growth_rate: SourceValue, net_growth_rate_timespan: SourceObject):
        super().__init__(
            name, usage_journey, devices, network, country,
            SourceHourlyValues(pd.DataFrame.from_records([{"value": 0}])))

        self.start_date = start_date.set_label(f"{self.name} start date")
        self.modeling_duration = modeling_duration.set_label(f"{self.name} modeling duration")
        self.initial_usage_journey_volume = initial_usage_journey_volume.set_label(
            f"{self.name} initial usage journey volume")
        self.initial_usage_journey_volume_timespan = initial_usage_journey_volume_timespan.set_label(
            f"{self.name} initial usage journey volume timespan")
        self.net_growth_rate = net_growth_rate.set_label(f"{self.name} net growth rate in percentage")
        self.net_growth_rate_timespan = net_growth_rate_timespan.set_label(f"{self.name} net growth rate timespan")
        self.initial_daily_usage_journey_volume = EmptyExplainableObject()
        self.daily_growth_rate = EmptyExplainableObject()

    @property
    def calculated_attributes(self) -> List[str]:
        return (["initial_daily_usage_journey_volume", "daily_growth_rate", "hourly_usage_journey_starts"]
                + super().calculated_attributes)

    def _timestamp_sourceobject_to_explainable_quantity(self, timestamp_sourceobject: SourceObject):
        unit_mapping = {"daily": u.day, "weekly": u.week, "monthly": u.month, "yearly": u.year}
        timespan_unit = unit_mapping[timestamp_sourceobject.value.lower()]
        timespan = ExplainableQuantity(
            1 * timespan_unit, label=f"1 {timespan_unit}").generate_explainable_object_with_logical_dependency(
            timestamp_sourceobject)

        return timespan

    def update_initial_daily_usage_journey_volume(self):
        timespan = self._timestamp_sourceobject_to_explainable_quantity(self.initial_usage_journey_volume_timespan)
        init_vol = self.initial_usage_journey_volume / timespan

        self.initial_daily_usage_journey_volume = init_vol.to("1/day").set_label(
            f"{self.name} initial daily usage journey volume")

    def update_daily_growth_rate(self):
        timespan = self._timestamp_sourceobject_to_explainable_quantity(self.net_growth_rate_timespan)

        daily_rate = (1 + self.net_growth_rate.to(u.dimensionless).magnitude) ** (1 / timespan.to(u.day).magnitude)

        self.daily_growth_rate = ExplainableQuantity(
            daily_rate * u.dimensionless, left_parent=self.net_growth_rate, right_parent=timespan,
            operator="combined and converted to daily growth rate").set_label(f"{self.name} daily growth rate")

    def update_hourly_usage_journey_starts(self):
        num_days = self.modeling_duration.to(u.day).magnitude
        days = np.arange(num_days)

        # Compute the daily usage journeys (daily constant value) with exponential growth.
        # Each day, the volume grows by daily_rate from the previous day.
        daily_values = (
            self.initial_daily_usage_journey_volume.to(1 / u.day).magnitude * self.daily_growth_rate.magnitude ** days)

        # Since the exponential growth is computed daily,
        # each day’s hourly value remains constant (daily value divided equally among 24 hours).
        hourly_values = np.repeat(daily_values / 24, 24)

        start = pd.to_datetime(self.start_date)
        hourly_index = pd.date_range(start=start, periods=len(hourly_values), freq='h')
        values_df = pd.DataFrame({"value": hourly_values}, index=hourly_index, dtype=f"pint[]")

        self.hourly_usage_journey_starts = ExplainableHourlyQuantities(
            values_df, left_parent=self.initial_daily_usage_journey_volume, right_parent=self.daily_growth_rate,
            operator="exponentially growing with daily rate"
        ).generate_explainable_object_with_logical_dependency(
            self.start_date
        ).generate_explainable_object_with_logical_dependency(
            self.modeling_duration
        ).set_label(
            f"{self.name} hourly usage journey starts")


@time_it
def compute_usage_journeys(
    start_date: str,
    initial_volume: float,
    initial_volume_timespan: str,  # "monthly" or "yearly"
    net_growth_rate: float,
    net_growth_rate_timespan: str,  # "monthly" or "yearly"
    num_days: int = 30  # duration of projection in days
) -> pd.DataFrame:
    """
    Computes an exponentially growing hourly series of usage journeys.

    Parameters:
      - start_date: The starting date (str) for the time series.
      - initial_volume: The volume of usage journeys defined over the given initial_volume_timespan.
      - initial_volume_timespan: The timespan for the initial volume; either "monthly" or "yearly".
      - net_growth_rate: The net growth rate over the period defined by net_growth_rate_timespan (e.g., 0.1 for 10%).
      - net_growth_rate_timespan: The timespan for the growth rate; either "monthly" or "yearly".
      - num_days: Number of days to project (default is 30).

    Returns:
      A pandas DataFrame with an hourly DateTimeIndex (starting at start_date) and a column "value"
      representing the exponentially growing hourly number of usage journeys. Growth is computed
      daily (i.e. each day’s hourly value is constant).
    """
    # Convert start_date to pandas Timestamp
    start = pd.to_datetime(start_date)

    # Convert initial volume to a daily rate using Pint.
    # initial_volume is provided per given timespan; we convert it to journeys/day.
    if initial_volume_timespan.lower() == "monthly":
        init_vol = (initial_volume * u.dimensionless) / u.month
    elif initial_volume_timespan.lower() == "yearly":
        init_vol = (initial_volume * u.dimensionless) / u.year
    else:
        raise ValueError("initial_volume_timespan must be 'monthly' or 'yearly'")

    # Convert to journeys per day (numerical value)
    init_daily = init_vol.to("1/day").magnitude

    # Determine the number of days in the growth rate period.
    if net_growth_rate_timespan.lower() == "monthly":
        period_days = (1 * u.month).to("day").magnitude
    elif net_growth_rate_timespan.lower() == "yearly":
        period_days = (1 * u.year).to("day").magnitude
    else:
        raise ValueError("net_growth_rate_timespan must be 'monthly' or 'yearly'")

    # Compute the effective daily growth rate.
    daily_rate = (1 + net_growth_rate) ** (1 / period_days) - 1

    # Create an array for each day index.
    days = np.arange(num_days)
    # Compute the daily usage journeys (daily constant value) with exponential growth.
    # Each day, the volume grows by (1+daily_rate) from the previous day.
    daily_values = init_daily * (1 + daily_rate) ** days

    # Since the exponential growth is computed daily,
    # each day’s hourly value remains constant (daily value divided equally among 24 hours).
    hourly_values = np.repeat(daily_values / 24, 24)

    # Create an hourly DateTimeIndex starting at start_date.
    hourly_index = pd.date_range(start=start, periods=len(hourly_values), freq='h')
    df = pd.DataFrame({"value": hourly_values}, index=hourly_index)

    return df


# Example usage:
if __name__ == "__main__":
    df = compute_usage_journeys(
        start_date="2025-01-01",
        initial_volume=10000,
        initial_volume_timespan="monthly",
        net_growth_rate=0.1,  # 10% growth rate
        net_growth_rate_timespan="yearly",
        num_days=5 * 365
    )
    print(df.head(30))
