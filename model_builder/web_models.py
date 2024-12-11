import json
import os

from efootprint.api_utils.json_to_system import json_to_system

from e_footprint_interface import settings
from model_builder.web_efootprint_wrappers import wrap_efootprint_object
from utils import EFOOTPRINT_COUNTRIES


class ModelWeb:
    def __init__(self, jsondata):
        self.jsondata = jsondata
        self.response_objs, self.flat_obj_dict = json_to_system(jsondata)
        self.system = wrap_efootprint_object(list(self.response_objs["System"].values())[0], self)

        for obj_id, mod_obj in self.flat_obj_dict.items():
            self.flat_obj_dict[obj_id] = wrap_efootprint_object(mod_obj, self)

        for obj_type in self.response_objs.keys():
            for obj_id, mod_obj in self.response_objs[obj_type].items():
                self.response_objs[obj_type][obj_id] = wrap_efootprint_object(mod_obj, self)

        with open(os.path.join(settings.BASE_DIR, 'theme', 'static', 'object_inputs_and_default_values.json'),
                  "r") as object_inputs_file:
            self.object_inputs_and_default_values = json.load(object_inputs_file)

    def get_objects_from_type(self, obj_type):
        return list(self.response_objs[obj_type].values())

    def get_object_from_id(self, object_id):
        return self.flat_obj_dict[object_id]

    def get_object_structure(self, object_type):
        return ObjectStructure(self, object_type)

    @property
    def storage(self):
        return self.get_objects_from_type("Storage")

    @property
    def servers(self):
        servers = []

        for server_type in ["Autoscaling", "OnPremise", "Serverless"]:
            if server_type in self.response_objs.keys():
                servers += self.response_objs[server_type].values()

        return servers

    @property
    def autoscaling_servers(self):
        return self.get_objects_from_type("Autoscaling")

    @property
    def on_premise_servers(self):
        return self.get_objects_from_type("OnPremise")

    @property
    def serverless_servers(self):
        return self.get_objects_from_type("Serverless")

    @property
    def jobs(self):
        return self.get_objects_from_type("Job")

    @property
    def uj_steps(self):
        return self.get_objects_from_type("UserJourneyStep")

    @property
    def user_journeys(self):
        return self.get_objects_from_type("UserJourney")

    @property
    def countries(self):
        return self.get_objects_from_type("Country")

    @property
    def available_countries(self):
        return EFOOTPRINT_COUNTRIES

    @property
    def hardware(self):
        return self.get_objects_from_type("Hardware")

    @property
    def networks(self):
        return self.get_objects_from_type("Network")

    @property
    def usage_patterns(self):
        return self.get_objects_from_type("UsagePattern")


class ObjectStructure:
    def __init__(self, model_web: ModelWeb, object_type: str):
        self.model_web = model_web
        self.object_type = object_type
        self.default_name = f"My new {object_type}"
        self.structure_dict = model_web.object_inputs_and_default_values[object_type]

    def __getattr__(self, name):
        attr = getattr(self.structure_dict, name)

        return attr

    @property
    def numerical_attributes(self):
        return self.structure_dict["numerical_attributes"]

    @property
    def modeling_obj_attributes(self):
        modeling_obj_attributes = self.structure_dict["modeling_obj_attributes"]

        for mod_obj_attribute_desc in modeling_obj_attributes:
            if mod_obj_attribute_desc["object_type"] == "Country":
                mod_obj_attribute_desc["existing_objects"] = [
                    country.to_json() for country in EFOOTPRINT_COUNTRIES]
            else:
                mod_obj_attribute_desc["existing_objects"] = self.model_web.get_objects_from_type(self.object_type)

        return modeling_obj_attributes

    @property
    def list_attributes(self):
        list_attributes = self.structure_dict["list_attributes"]

        for list_attribute_desc in list_attributes:
            if list_attribute_desc["object_type"] == "Country":
                list_attribute_desc["existing_objects"] = [
                    country.to_json() for country in EFOOTPRINT_COUNTRIES]
            else:
                list_attribute_desc["existing_objects"] = self.model_web.get_objects_from_type(self.object_type)

        return list_attributes

    @property
    def all_attribute_names(self):
        all_attribute_names = []
        for attribute_type in self.structure_dict.keys():
            for attribute in self.structure_dict[attribute_type]:
                all_attribute_names.append(attribute["attr_name"])

        return all_attribute_names
