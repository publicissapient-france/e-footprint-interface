from unittest import TestCase
from unittest.mock import MagicMock

from efootprint.core.country import Country
from efootprint.core.hardware.device import Device
from efootprint.core.usage.usage_journey import UsageJourney
from efootprint.utils.calculus_graph import build_calculus_graph
from efootprint.core.hardware.network import Network

from model_builder.efootprint_extensions.usage_pattern_from_form import UsagePatternFromForm


class CalculusGraphTest(TestCase):
    def test_calculus_graph_html_gen(self):
        self.mock_usage_journey = MagicMock(spec=UsageJourney, id="usage-journey-id")
        self.mock_devices = [MagicMock(spec=Device, id="device-id"), MagicMock(spec=Device, id="device-id2")]
        self.mock_network = MagicMock(spec=Network, id="network-id")
        self.mock_country = MagicMock(spec=Country, id="FR-id")

        self.usage_pattern = UsagePatternFromForm.from_defaults(
            name="test_usage_pattern_from_form",
            usage_journey=self.mock_usage_journey,
            devices=self.mock_devices,
            network=self.mock_network,
            country=self.mock_country
        )

        # To get calculated attributes
        calculated_attributes = self.usage_pattern.calculated_attributes

        # To get calculus graph html
        self.usage_pattern.update_daily_growth_rate()

        calculus_graph = build_calculus_graph(self.usage_pattern.daily_growth_rate)
        calculus_graph.cdn_resources = "remote"
        html = calculus_graph.generate_html()
        self.assertGreater(len(html), 0)
