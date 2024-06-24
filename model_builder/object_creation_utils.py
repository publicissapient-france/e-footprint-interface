# Important to keep these imports because they constitute the globals() dict
from efootprint.core.service import Service
from efootprint.core.system import System
from efootprint.core.hardware.storage import Storage
from efootprint.core.hardware.servers.autoscaling import Autoscaling
from efootprint.core.hardware.servers.serverless import Serverless
from efootprint.core.hardware.servers.on_premise import OnPremise
from efootprint.core.hardware.hardware_base_classes import Hardware
from efootprint.core.usage.usage_pattern import UsagePattern
from efootprint.core.usage.user_journey import UserJourney
from efootprint.core.usage.user_journey import UserJourneyStep
from efootprint.core.hardware.network import Network
from efootprint.core.hardware.device_population import DevicePopulation
from efootprint.constants.countries import Country
from efootprint.abstract_modeling_classes.source_objects import SourceValue, SourceObject, Sources
from efootprint.constants.units import u
from efootprint.logger import logger
from utils import EFOOTPRINT_COUNTRIES

from django.conf import settings
import json
import os


def create_efootprint_obj_from_post_data(request, flat_obj_dict):
    with open(os.path.join(settings.BASE_DIR, 'theme', 'static', 'object_inputs_and_default_values.json'), "r") as file:
        obj_inputs_and_default_values = json.load(file)

    new_efootprint_obj_class = globals()[request.POST["obj_type"]]
    new_efootprint_obj = new_efootprint_obj_class.__new__(new_efootprint_obj_class)

    obj_creation_kwargs = {}
    obj_inputs = obj_inputs_and_default_values[request.POST["obj_type"]]
    obj_creation_kwargs["name"] = request.POST["name"]
    for attr_dict in obj_inputs["numerical_attributes"]:
        assert request.POST.getlist(attr_dict["attr_name"])[1] == attr_dict["unit"]
        obj_creation_kwargs[attr_dict["attr_name"]] = SourceValue(
            float(request.POST.getlist(attr_dict["attr_name"])[0]) * u(attr_dict["unit"]))
    for mod_obj in obj_inputs["modeling_obj_attributes"]:
        new_mod_obj_id = request.POST[mod_obj["attr_name"]]
        if mod_obj["object_type"] == "Country" and new_mod_obj_id not in flat_obj_dict.keys():
            obj_to_add = [country for country in EFOOTPRINT_COUNTRIES if country.id == new_mod_obj_id][0]
            request.session["system_data"]["Country"][new_mod_obj_id] = obj_to_add.to_json()
        else:
            obj_to_add = flat_obj_dict[new_mod_obj_id]
        obj_creation_kwargs[mod_obj["attr_name"]] = obj_to_add
    for mod_obj in obj_inputs["list_attributes"]:
        obj_creation_kwargs[mod_obj["attr_name"]] = [
            flat_obj_dict[obj_id] for obj_id in request.POST.getlist(mod_obj["attr_name"])]
    if request.POST["obj_type"] == "UsagePattern":
        obj_creation_kwargs["time_intervals"] = SourceObject([[7, 12], [18, 23]])

    new_efootprint_obj.__init__(**obj_creation_kwargs)

    return new_efootprint_obj


def add_new_object_to_system(request, response_objs, flat_obj_dict):
    new_efootprint_obj = create_efootprint_obj_from_post_data(request, flat_obj_dict)

    # If object is a usage pattern it has to be added to the System to trigger recomputation
    system = list(response_objs["System"].values())[0]
    if request.POST["obj_type"] == "UsagePattern":
        system.usage_patterns += [new_efootprint_obj]
        request.session["system_data"]["System"][system.id]["usage_patterns"] = [up.id for up in system.usage_patterns]
    else:
        new_efootprint_obj.launch_attributes_computation_chain()

    # Update session data
    request.session["system_data"][request.POST["obj_type"]][new_efootprint_obj.id] = new_efootprint_obj.to_json()
    # Here we updated a sub dict of request.session so we have to explicitly tell Django that it has been updated
    request.session.modified = True

    # Add new object to object dict to recompute context
    response_objs[request.POST["obj_type"]][new_efootprint_obj.id] = new_efootprint_obj

    objects_to_update = []
    if request.POST["obj_type"] == "UsagePattern":
        # Special case where adding a UsagePattern makes all UsagePatterns deletable and thus need to be updated
        for up in system.usage_patterns:
            if up.id != new_efootprint_obj.id:
                objects_to_update.append(up)

    return new_efootprint_obj, system, objects_to_update


def edit_object_in_system(request, response_objs, flat_obj_dict):
    obj_to_edit = flat_obj_dict[request.POST["obj_id"]]

    with open(os.path.join(settings.BASE_DIR, 'theme', 'static', 'object_inputs_and_default_values.json'), "r") as file:
        obj_inputs_and_default_values = json.load(file)

    obj_inputs = obj_inputs_and_default_values[request.POST["obj_type"]]

    obj_to_edit.name = request.POST["name"]
    objects_to_update = [obj_to_edit]
    obj_ids_of_connections_to_add = []
    obj_ids_of_connections_to_remove = []

    for attr_dict in obj_inputs["numerical_attributes"]:
        request_value = request.POST.getlist(attr_dict["attr_name"])[0]
        request_unit = request.POST.getlist(attr_dict["attr_name"])[1]
        new_value = SourceValue(float(request_value) * u(request_unit), Sources.USER_DATA)
        current_value = getattr(obj_to_edit, attr_dict["attr_name"])
        if new_value != current_value:
            logger.info(f"{attr_dict['attr_name']} has changed")
            new_value.set_label(current_value.label)
            obj_to_edit.__setattr__(attr_dict["attr_name"], new_value)
    for mod_obj in obj_inputs["modeling_obj_attributes"]:
        new_mod_obj_id = request.POST[mod_obj["attr_name"]]
        current_mod_obj_id = getattr(obj_to_edit, mod_obj["attr_name"]).id
        if new_mod_obj_id != current_mod_obj_id:
            logger.info(f"{mod_obj['attr_name']} has changed")
            if mod_obj["object_type"] == "Country" and new_mod_obj_id not in flat_obj_dict.keys():
                obj_to_add = [country for country in EFOOTPRINT_COUNTRIES if country.id == new_mod_obj_id][0]
                request.session["system_data"]["Country"][new_mod_obj_id] = obj_to_add.to_json()
            else:
                obj_to_add = flat_obj_dict[new_mod_obj_id]
                objects_to_update.append(obj_to_add)
                obj_ids_of_connections_to_add.append(new_mod_obj_id)
            obj_to_edit.__setattr__(mod_obj["attr_name"], obj_to_add)
            obj_ids_of_connections_to_remove.append(current_mod_obj_id)
    for mod_obj in obj_inputs["list_attributes"]:
        new_mod_obj_id_list = request.POST.getlist(mod_obj["attr_name"])
        current_mod_obj_id_list = [mod_obj.id for mod_obj in getattr(obj_to_edit, mod_obj["attr_name"])]
        logger.info(f"{mod_obj['attr_name']} has changed")
        removed_mod_obj_ids = [id for id in current_mod_obj_id_list if id not in new_mod_obj_id_list]
        added_mod_obj_ids = [id for id in new_mod_obj_id_list if id not in current_mod_obj_id_list]
        obj_ids_of_connections_to_add += added_mod_obj_ids
        obj_ids_of_connections_to_remove += removed_mod_obj_ids
        for mod_obj_id in removed_mod_obj_ids + added_mod_obj_ids:
            # Changed list attributes are updated because their deletability might have changed
            objects_to_update.append(flat_obj_dict[mod_obj_id])
        if new_mod_obj_id_list != current_mod_obj_id_list:
            obj_to_edit.__setattr__(mod_obj["attr_name"], [flat_obj_dict[obj_id] for obj_id in new_mod_obj_id_list])

    # Update session data
    request.session["system_data"][request.POST["obj_type"]][obj_to_edit.id] = obj_to_edit.to_json()
    # Here we updated a sub dict of request.session so we have to explicitly tell Django that it has been updated
    request.session.modified = True

    return (obj_to_edit, list(response_objs["System"].values())[0], objects_to_update, obj_ids_of_connections_to_add,
            obj_ids_of_connections_to_remove)
