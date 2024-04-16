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


from django.conf import settings
import json
import os


def create_efootprint_obj_from_post_data(request, flat_obj_dict):
    with open(os.path.join(settings.BASE_DIR, 'object_inputs_and_default_values.json'), "r") as file:
        obj_inputs_and_default_values = json.load(file)

    new_efootprint_obj_class = globals()[request.POST["obj_type"]]
    new_efootprint_obj = new_efootprint_obj_class.__new__(new_efootprint_obj_class)

    obj_creation_kwargs = {}
    obj_inputs = obj_inputs_and_default_values[request.POST["obj_type"]]
    obj_creation_kwargs["name"] = request.POST["name"]
    for attr_dict in obj_inputs["numerical_attributes"]:
        obj_creation_kwargs[attr_dict["attr_name"]] = SourceValue(
            float(request.POST[attr_dict["attr_name"]]) * u(attr_dict["unit"]))
    for mod_obj in obj_inputs["modeling_obj_attributes"]:
        obj_creation_kwargs[mod_obj["attr_name"]] = flat_obj_dict[request.POST[mod_obj["attr_name"]]]
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
    if request.POST["obj_type"] == "UsagePattern":
        system = list(response_objs["System"].values())[0]
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

    return response_objs


def edit_object_in_system(request, response_objs, flat_obj_dict):
    obj_to_edit = flat_obj_dict[request.POST["obj_id"]]

    with open(os.path.join(settings.BASE_DIR, 'object_inputs_and_default_values.json'), "r") as file:
        obj_inputs_and_default_values = json.load(file)

    obj_inputs = obj_inputs_and_default_values[request.POST["obj_type"]]

    obj_to_edit.name = request.POST["name"]

    for attr_dict in obj_inputs["numerical_attributes"]:
        new_value = SourceValue(
            float(request.POST[attr_dict["attr_name"]]) * u(attr_dict["unit"]), Sources.USER_DATA)
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
            obj_to_edit.__setattr__(mod_obj["attr_name"], flat_obj_dict[new_mod_obj_id])
    for mod_obj in obj_inputs["list_attributes"]:
        new_mod_obj_id_list = request.POST.getlist(mod_obj["attr_name"])
        current_mod_obj_id_list = [mod_obj.id for mod_obj in getattr(obj_to_edit, mod_obj["attr_name"])]
        logger.info(f"{mod_obj['attr_name']} has changed")
        if new_mod_obj_id_list != current_mod_obj_id_list:
            obj_to_edit.__setattr__(mod_obj["attr_name"], [flat_obj_dict[obj_id] for obj_id in new_mod_obj_id_list])

    # Update session data
    request.session["system_data"][request.POST["obj_type"]][obj_to_edit.id] = obj_to_edit.to_json()
    # Here we updated a sub dict of request.session so we have to explicitly tell Django that it has been updated
    request.session.modified = True

    return response_objs
