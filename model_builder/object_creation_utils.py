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
from efootprint.abstract_modeling_classes.source_objects import SourceValue, SourceObject
from efootprint.constants.units import u


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
