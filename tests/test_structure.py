import os
import re
import json
from unittest import TestCase
from unittest.mock import Mock

from efootprint.api_utils.json_to_system import modeling_object_classes_dict
from efootprint.core.all_classes_in_order import SERVICE_CLASSES, SERVER_CLASSES, SERVICE_JOB_CLASSES, \
    SERVER_BUILDER_CLASSES
from efootprint.core.hardware.hardware import Hardware
from efootprint.core.hardware.network import Network
from efootprint.core.usage.job import Job

from model_builder.class_structure import efootprint_class_structure, generate_object_creation_structure
from model_builder.model_web import ModelWeb, ObjectStructure, model_web_root
from utils import EFOOTPRINT_COUNTRIES


obj_creation_structure_dict = {
        "Service": SERVICE_CLASSES, "Server": SERVER_CLASSES + SERVER_BUILDER_CLASSES,
        "Job": [Job] + SERVICE_JOB_CLASSES}
root_dir = os.path.dirname(os.path.abspath(__file__))


class TestsClassStructure(TestCase):
    def test_class_creation_structures(self):
        for class_category_name, class_list in obj_creation_structure_dict.items():
            print(class_category_name)
            tmp_filepath = os.path.join(
                root_dir, "class_structures", f"{class_category_name}_creation_structure_tmp.json")
            with open(tmp_filepath, "w") as f:
                json.dump(generate_object_creation_structure(class_list, header=class_category_name), f, indent=4)

            with open(tmp_filepath, "r") as tmp_file, open(tmp_filepath.replace("_tmp", ""), "r") as ref_file:
                self.assertEqual(tmp_file.read(), ref_file.read())
                os.remove(tmp_filepath)

    def test_object_structures(self):
        for class_name in modeling_object_classes_dict.keys():
            obj_structure = efootprint_class_structure(class_name)
            with open(os.path.join(root_dir, "class_structures", f"{class_name}.json"), "r") as f:
                ref_structure = json.load(f)
            self.assertEqual(obj_structure, ref_structure)

    def test_all_attribute_names(self):
        model_web = Mock(spec=ModelWeb)
        for class_name in modeling_object_classes_dict.keys():
            print(class_name)
            obj_structure = ObjectStructure(model_web, class_name)
            all_attribute_names = obj_structure.all_attribute_names

    def test_default_objects(self):
        default_efootprint_networks = [network_archetype() for network_archetype in Network.archetypes()]
        default_efootprint_hardwares = [Hardware.laptop(), Hardware.smartphone()]

        network_archetypes = {network.id: network.to_json() for network in default_efootprint_networks}
        hardware_archetypes = {hardware.id: hardware.to_json() for hardware in default_efootprint_hardwares}
        countries = {country.id: country.to_json() for country in EFOOTPRINT_COUNTRIES}

        with open(os.path.join(model_web_root, "default_networks.json"), "r") as f:
            default_networks = json.load(f)
        with open(os.path.join(model_web_root, "default_hardwares.json"), "r") as f:
            default_hardwares = json.load(f)
        with open(os.path.join(model_web_root, "default_countries.json"), "r") as f:
            default_countries = json.load(f)

        def remove_ids_from_str(json_str):
            return re.sub(r"\"id-[a-zA-Z0-9]{6}-", "\"id-XXXXXX-", json_str)

        self.assertEqual(
            remove_ids_from_str(json.dumps(network_archetypes)), remove_ids_from_str(json.dumps(default_networks)))
        self.assertEqual(
            remove_ids_from_str(json.dumps(hardware_archetypes)), remove_ids_from_str(json.dumps(default_hardwares)))
        self.assertEqual(
            remove_ids_from_str(json.dumps(countries)), remove_ids_from_str(json.dumps(default_countries)))


if __name__ == "__main__":
    for class_category_name, class_list in obj_creation_structure_dict.items():
        print(class_category_name)
        with open(
            os.path.join(root_dir, "class_structures", f"{class_category_name}_creation_structure.json"), "w") as f:
            json.dump(generate_object_creation_structure(class_list, header=class_category_name), f, indent=4)

    for class_name in modeling_object_classes_dict.keys():
        print(class_name)
        with open(os.path.join(root_dir, "class_structures", f"{class_name}.json"), "w") as f:
            json.dump(efootprint_class_structure(class_name), f, indent=4)
