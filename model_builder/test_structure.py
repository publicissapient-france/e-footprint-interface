import re
import json
from unittest import TestCase

from efootprint.core.hardware.hardware import Hardware
from efootprint.core.hardware.network import Network

from model_builder.class_structure import efootprint_class_structure
from utils import EFOOTPRINT_COUNTRIES


class TestsClassStructure(TestCase):
    def test_services_structure(self):
        video_streaming_structure = efootprint_class_structure("VideoStreaming")
        genai_structure = efootprint_class_structure("GenAIModel")
        web_app_structure = efootprint_class_structure("WebApplication")
        a = 1

    def test_default_objects(self):
        default_efootprint_networks = [network_archetype() for network_archetype in Network.archetypes()]
        default_efootprint_hardwares = [Hardware.laptop(), Hardware.smartphone()]

        network_archetypes = {network.id: network.to_json() for network in default_efootprint_networks}
        hardware_archetypes = {hardware.id: hardware.to_json() for hardware in default_efootprint_hardwares}
        countries = {country.id: country.to_json() for country in EFOOTPRINT_COUNTRIES}

        with open("default_networks.json", "r") as f:
            default_networks = json.load(f)
        with open("default_hardwares.json", "r") as f:
            default_hardwares = json.load(f)
        with open("default_countries.json", "r") as f:
            default_countries = json.load(f)

        def remove_ids_from_str(json_str):
            return re.sub(r"\"id-[a-zA-Z0-9]{6}-", "\"id-XXXXXX-", json_str)

        self.assertEqual(
            remove_ids_from_str(json.dumps(network_archetypes)), remove_ids_from_str(json.dumps(default_networks)))
        self.assertEqual(
            remove_ids_from_str(json.dumps(hardware_archetypes)), remove_ids_from_str(json.dumps(default_hardwares)))
        self.assertEqual(
            remove_ids_from_str(json.dumps(countries)), remove_ids_from_str(json.dumps(default_countries)))

