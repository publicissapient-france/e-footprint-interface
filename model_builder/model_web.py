import json
import os
import re
from time import time

from django.contrib.sessions.backends.base import SessionBase
from efootprint.api_utils.json_to_system import json_to_system, json_to_explainable_object
from efootprint.core.all_classes_in_order import SERVER_CLASSES, SERVICE_CLASSES, SERVER_BUILDER_CLASSES
from efootprint.logger import logger

from model_builder.class_structure import MODELING_OBJECT_CLASSES_DICT
from model_builder.modeling_objects_web import wrap_efootprint_object
from utils import EFOOTPRINT_COUNTRIES

model_web_root = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(model_web_root, "default_networks.json"), "r") as f:
    DEFAULT_NETWORKS = json.load(f)
with open(os.path.join(model_web_root, "default_hardwares.json"), "r") as f:
    DEFAULT_HARDWARES = json.load(f)
with open(os.path.join(model_web_root, "default_countries.json"), "r") as f:
    DEFAULT_COUNTRIES = json.load(f)


DEFAULT_OBJECTS_CLASS_MAPPING = {
    "Network": DEFAULT_NETWORKS, "Hardware": DEFAULT_HARDWARES, "Country": DEFAULT_COUNTRIES}


class ModelWeb:
    def __init__(
        self, session_data: SessionBase, launch_system_computations=False, set_trigger_modeling_updates_to_false=True):
        start = time()
        self.system_data = session_data["system_data"]
        self.response_objs, self.flat_efootprint_objs_dict = json_to_system(
            self.system_data, launch_system_computations)
        self.empty_objects = session_data.get("empty_objects", {})
        self.system = wrap_efootprint_object(list(self.response_objs["System"].values())[0], self)
        if set_trigger_modeling_updates_to_false:
            self.set_all_trigger_modeling_updates_to_false()
        logger.info(f"ModelWeb object created in {time() - start:.3f} seconds.")

    def set_all_trigger_modeling_updates_to_false(self):
        self.system.set_efootprint_value("trigger_modeling_updates", False)
        for web_obj in self.system.all_linked_objects:
            web_obj.set_efootprint_value("trigger_modeling_updates", False)

    def get_efootprint_objects_from_efootprint_type(self, obj_type):
        if obj_type in self.response_objs.keys():
            return list(self.response_objs[obj_type].values())
        else:
            return []

    def get_web_objects_from_efootprint_type(self, obj_type):
        if obj_type in DEFAULT_OBJECTS_CLASS_MAPPING.keys():
            return DEFAULT_OBJECTS_CLASS_MAPPING[obj_type]

        return [wrap_efootprint_object(obj, self) for obj in self.get_efootprint_objects_from_efootprint_type(obj_type)]

    def get_web_object_from_efootprint_id(self, object_id):
        efootprint_object = self.flat_efootprint_objs_dict[object_id]
        return wrap_efootprint_object(efootprint_object, self)

    def get_efootprint_object_from_efootprint_id(
        self, efootprint_id: str, object_type: str, request_session: SessionBase):
        if efootprint_id in self.flat_efootprint_objs_dict.keys():
            efootprint_object = self.flat_efootprint_objs_dict[efootprint_id]
        else:
            from model_builder.object_creation_and_edition_utils import add_new_efootprint_object_to_system
            web_object_json = DEFAULT_OBJECTS_CLASS_MAPPING[object_type][efootprint_id]
            efootprint_class = MODELING_OBJECT_CLASSES_DICT[object_type]
            efootprint_object = efootprint_class.__new__(efootprint_class)
            efootprint_object.__dict__["contextual_modeling_obj_containers"] = []
            efootprint_object.trigger_modeling_updates = False
            for attr_key, attr_value in web_object_json.items():
                if type(attr_value) == dict:
                    efootprint_object.__setattr__(attr_key, json_to_explainable_object(attr_value))
                else:
                    efootprint_object.__dict__[attr_key] = attr_value
            efootprint_object.after_init()
            web_object = add_new_efootprint_object_to_system(request_session, self, efootprint_object)
            logger.info(f"Object {web_object.name} created from default object and added to system data.")

        return efootprint_object

    @property
    def storage(self):
        return self.get_web_objects_from_efootprint_type("Storage")

    @property
    def servers(self):
        servers = []

        for server_type in [server_class.__name__ for server_class in SERVER_CLASSES + SERVER_BUILDER_CLASSES]:
            servers += self.get_web_objects_from_efootprint_type(server_type)

        return servers

    @property
    def services(self):
        return sum(
            [self.get_web_objects_from_efootprint_type(service.__name__) for service in SERVICE_CLASSES], start=[])

    @property
    def cpu_servers(self):
        return self.get_web_objects_from_efootprint_type("Server")

    @property
    def gpu_servers(self):
        return self.get_web_objects_from_efootprint_type("GPUServer")

    @property
    def usage_journeys(self):
        return self.get_web_objects_from_efootprint_type("UsageJourney")

    @property
    def countries(self):
        return self.get_web_objects_from_efootprint_type("Country")

    @property
    def available_countries(self):
        return EFOOTPRINT_COUNTRIES

    @property
    def hardware(self):
        return self.get_web_objects_from_efootprint_type("Hardware")

    @property
    def networks(self):
        return self.get_web_objects_from_efootprint_type("Network")

    @property
    def usage_patterns(self):
        return self.get_web_objects_from_efootprint_type("UsagePattern")

    @property
    def empty_usage_journeys(self):
        if "UsageJourney" in self.empty_objects.keys():
            return self.empty_objects["UsageJourney"].values()
        else:
            return []

    @property
    def system_emissions(self):
        emissions = {}
        for energy_row in self.system.total_energy_footprints:
            emissions[f"{energy_row}_energy"] = self.system.total_energy_footprints[energy_row].to_json()

        for fabrication_row in self.system.total_fabrication_footprints:
            emissions[f"{fabrication_row}_fabrication"] = self.system.total_energy_footprints[
                fabrication_row].to_json()

        return emissions
