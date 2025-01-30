import re

from django.contrib.sessions.backends.base import SessionBase
from efootprint.api_utils.json_to_system import json_to_system
from efootprint.core.all_classes_in_order import SERVER_CLASSES, SERVICE_CLASSES

from model_builder.class_structure import efootprint_class_structure
from model_builder.modeling_objects_web import wrap_efootprint_object
from utils import EFOOTPRINT_COUNTRIES


class ModelWeb:
    def __init__(self, session_data: SessionBase):
        self.system_data = session_data["system_data"]
        self.response_objs, self.flat_efootprint_objs_dict = json_to_system(self.system_data)
        self.empty_objects = session_data.get("empty_objects", {})
        self.system = wrap_efootprint_object(list(self.response_objs["System"].values())[0], self)

    def get_efootprint_objects_from_efootprint_type(self, obj_type):
        if obj_type in self.response_objs.keys():
            return list(self.response_objs[obj_type].values())
        else:
            return []

    def get_web_objects_from_efootprint_type(self, obj_type):
        return [wrap_efootprint_object(obj, self) for obj in self.get_efootprint_objects_from_efootprint_type(obj_type)]

    def get_web_object_from_efootprint_id(self, object_id):
        efootprint_object = self.flat_efootprint_objs_dict[object_id]
        return wrap_efootprint_object(efootprint_object, self)

    def get_efootprint_object_from_efootprint_id(
        self, new_mod_obj_id: str, object_type: str, request_session: SessionBase):
        # TODO for DEVICES, HARDWARE and NETWORK, STORAGE ?
        if object_type == "Country" and new_mod_obj_id not in self.flat_efootprint_objs_dict.keys():
            obj_to_add = [country for country in EFOOTPRINT_COUNTRIES if country.id == new_mod_obj_id][0]
            request_session["system_data"]["Country"][new_mod_obj_id] = obj_to_add.to_json()
            request_session.modified = True
        else:
            obj_to_add = self.flat_efootprint_objs_dict[new_mod_obj_id]

        return obj_to_add

    def get_object_structure(self, object_type):
        return ObjectStructure(self, object_type)

    @property
    def storage(self):
        return self.get_web_objects_from_efootprint_type("Storage")

    @property
    def servers(self):
        servers = []

        for server_type in [server_class.__name__ for server_class in SERVER_CLASSES]:
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


class ObjectStructure:
    def __init__(self, model_web: ModelWeb, object_type: str):
        self.model_web = model_web
        self.object_type = object_type
        self.default_name = f"My new {object_type}"
        self.structure_dict = efootprint_class_structure(object_type)

    def __getattr__(self, name):
        attr = getattr(self.structure_dict, name)

        return attr

    @property
    def numerical_attributes(self):
        return self.structure_dict.get("numerical_attributes", [])

    @property
    def hourly_quantities_attributes(self):
        return self.structure_dict.get("hourly_quantities_attributes", [])

    @property
    def str_attributes(self):
        return self.structure_dict.get("str_attributes", {})

    @property
    def conditional_str_attributes(self):
        return self.structure_dict.get("conditional_str_attributes", {})

    @property
    def modeling_obj_attributes(self):
        modeling_obj_attributes = self.structure_dict.get("modeling_obj_attributes", [])

        for mod_obj_attribute_desc in modeling_obj_attributes:
            if mod_obj_attribute_desc["object_type"] == "Country":
                mod_obj_attribute_desc["existing_objects"] = [
                    country.to_json() for country in EFOOTPRINT_COUNTRIES]
            else:
                mod_obj_attribute_desc["existing_objects"] = self.model_web.get_web_objects_from_efootprint_type(
                    mod_obj_attribute_desc["object_type"])

        return modeling_obj_attributes

    @property
    def list_attributes(self):
        list_attributes = self.structure_dict.get("list_attributes", [])

        for list_attribute_desc in list_attributes:
            if list_attribute_desc["object_type"] == "Country":
                list_attribute_desc["existing_objects"] = [
                    country.to_json() for country in EFOOTPRINT_COUNTRIES]
            else:
                list_attribute_desc["existing_objects"] = self.model_web.get_web_objects_from_efootprint_type(list_attribute_desc["object_type"])

        return list_attributes

    @property
    def all_attribute_names(self):
        all_attribute_names = []
        for attribute_type in self.structure_dict.keys():
            for attribute in self.structure_dict[attribute_type]:
                all_attribute_names.append(attribute["attr_name"])

        return all_attribute_names

    @property
    def template_name(self):
        snake_case_class_name = re.sub(r'(?<!^)(?=[A-Z])', '_', self.object_type).lower()
        return f"{snake_case_class_name}"
