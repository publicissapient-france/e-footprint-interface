from datetime import datetime
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


class UsagePatternFromForm(UsagePattern):
    @classmethod
    def default_values(cls):
        return {
            "start_date": SourceObject("2025-01-01"),
            "modeling_duration": SourceValue(365 * u.day),
            "initial_usage_journey_volume": SourceValue(10000 * u.dimensionless),
            "initial_usage_journey_volume_timespan": SourceObject("monthly"),
            "net_growth_rate": SourceValue(0.1 * u.dimensionless),
            "net_growth_rate_timespan": SourceObject("yearly")
        }
    @classmethod
    def list_values(cls):
        return {
            "initial_usage_journey_volume_timespan": [
                SourceObject("daily"), SourceObject("monthly"), SourceObject("yearly")],
        }

    @classmethod
    def conditional_list_values(cls):
        return {
            "net_growth_rate_timespan": {
                "depends_on": "initial_usage_journey_volume_timespan",
                "conditional_list_values": {
                    SourceObject("daily"): [SourceObject("monthly"), SourceObject("yearly")],
                    SourceObject("monthly"): [SourceObject("monthly"), SourceObject("yearly")],
                    SourceObject("yearly"): [SourceObject("yearly")]
                }
            }
        }

    def __init__(self, name: str, usage_journey: UsageJourney, devices: List[Device],
                 network: Network, country: Country, start_date: SourceObject, modeling_duration: SourceValue,
                 initial_usage_journey_volume: SourceValue, initial_usage_journey_volume_timespan: SourceObject,
                 net_growth_rate: SourceValue, net_growth_rate_timespan: SourceObject):
        super().__init__(
            name, usage_journey, devices, network, country,
            SourceHourlyValues(pd.DataFrame({"value": [0]}, dtype=f"pint[]")))

        self.start_date = start_date.set_label(f"{self.name} start date")
        self.modeling_duration = modeling_duration.set_label(f"{self.name} modeling duration")
        self.initial_usage_journey_volume = initial_usage_journey_volume.set_label(
            f"{self.name} initial usage journey volume")
        self.initial_usage_journey_volume_timespan = initial_usage_journey_volume_timespan.set_label(
            f"{self.name} initial usage journey volume timespan")
        self.net_growth_rate = net_growth_rate.set_label(f"{self.name} net growth rate in percentage")
        self.net_growth_rate_timespan = net_growth_rate_timespan.set_label(f"{self.name} net growth rate timespan")
        self.first_daily_usage_journey_volume = EmptyExplainableObject()
        self.daily_growth_rate = EmptyExplainableObject()

    @property
    def calculated_attributes(self) -> List[str]:
        return (["first_daily_usage_journey_volume", "daily_growth_rate", "hourly_usage_journey_starts"]
                + super().calculated_attributes)

    @staticmethod
    def _timestamp_sourceobject_to_explainable_quantity(timestamp_sourceobject: SourceObject):
        unit_mapping = {"daily": u.day, "weekly": u.week, "monthly": u.month, "yearly": u.year}
        timespan_unit = unit_mapping[timestamp_sourceobject.value.lower()]
        timespan = ExplainableQuantity(
            1 * timespan_unit, label=f"1 {timespan_unit}").generate_explainable_object_with_logical_dependency(
            timestamp_sourceobject)

        return timespan

    def update_first_daily_usage_journey_volume(self):
        timespan = self._timestamp_sourceobject_to_explainable_quantity(self.initial_usage_journey_volume_timespan)
        init_vol = self.initial_usage_journey_volume / timespan

        self.first_daily_usage_journey_volume = init_vol.to("1/day").set_label(
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
            self.first_daily_usage_journey_volume.to(1 / u.day).magnitude * self.daily_growth_rate.magnitude ** days)

        # Since the exponential growth is computed daily,
        # each day’s hourly value remains constant (daily value divided equally among 24 hours).
        hourly_values = np.repeat(daily_values / 24, 24)

        start = datetime.strptime(self.start_date.value, "%Y-%m-%d")
        hourly_index = pd.period_range(start=start, periods=len(hourly_values), freq='h')
        values_df = pd.DataFrame({"value": hourly_values}, index=hourly_index, dtype=f"pint[]")

        self.hourly_usage_journey_starts = ExplainableHourlyQuantities(
            values_df, left_parent=self.first_daily_usage_journey_volume, right_parent=self.daily_growth_rate,
            operator="exponentially growing with daily rate"
        ).generate_explainable_object_with_logical_dependency(
            self.start_date
        ).generate_explainable_object_with_logical_dependency(
            self.modeling_duration
        ).set_label(
            f"{self.name} hourly usage journey starts")
