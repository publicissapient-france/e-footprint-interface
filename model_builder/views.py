from efootprint.api_utils.json_to_system import json_to_system
from efootprint.abstract_modeling_classes.explainable_objects import ExplainableQuantity
from efootprint.abstract_modeling_classes.modeling_object import ModelingObject
from efootprint.api_utils.system_to_json import system_to_json
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

from utils import htmx_render

from django.conf import settings
import json
from django.shortcuts import render
from django.utils.datastructures import MultiValueDictKeyError
import os


def model_builder_main(request):
    try:
        jsondata = json.loads(request.POST["json"])
    except MultiValueDictKeyError:
        if "system_data" not in request.session.keys():
            with open(os.path.join("model_builder", "default_system_data.json"), "r") as file:
                jsondata = json.load(file)
                request.session["system_data"] = jsondata
        else:
            jsondata = request.session["system_data"]

    # compute calculated attributes with e-footprint
    context = get_context_from_json(jsondata)
    system_footprint_html = context["System"][0]["object"].plot_footprints_by_category_and_object()._repr_html_()

    return htmx_render(
        request, "model_builder/model-builder-main.html",
        context={"context": context, "systemFootprint": system_footprint_html})


def update_value(request):
    object_type = request.POST["key"]
    object_name = request.POST["e-footprint-obj"]
    attr_name = request.POST["attr_name"]
    request.session["system_data"][object_type][object_name][attr_name]["value"] = float(request.POST["value"])
    request.session.modified = True
    context = get_context_from_json(request.session["system_data"])

    system_footprint_html = context["System"][0]["object"].plot_footprints_by_category_and_object()._repr_html_()

    return render(
        request, "model_builder/graph-container.html",
        context={"context": context, "systemFootprint": system_footprint_html})


def open_add_new_object_panel(request):
    context = get_context_from_json(request.session["system_data"])

    object_type = request.GET["obj"]
    object_inputs_file = open(os.path.join(settings.BASE_DIR, 'object_inputs_and_default_values.json'))
    object_inputs_and_default_values = json.load(object_inputs_file)
    numerical_attributes = object_inputs_and_default_values[object_type]["numerical_attributes"]
    modeling_obj_attributes = object_inputs_and_default_values[object_type]["modeling_obj_attributes"]
    list_attributes = object_inputs_and_default_values[object_type]["list_attributes"]

    context_data = {
        "obj_name": request.GET["obj"], "display_obj_form": True,
        "numerical_attributes": numerical_attributes,
        "modeling_obj_attributes": modeling_obj_attributes,
        "list_attributes": list_attributes,
        "object_types": {}
    }
    for object_type in modeling_obj_attributes:
        context_data["object_types"][object_type["object_type"]] = [
            data["object"] for data in context[object_type["object_type"]]]

    if list_attributes:
        for object_type in list_attributes:
            context_data["object_types"][object_type["object_type"]] = [
                data["object"] for data in context[object_type["object_type"]]]

    return render(request, "model_builder/object-creation-form.html", context=context_data)


def add_new_object(request):
    new_obj = {}
    for key, value in request.POST.items():
        new_obj[key] = value

    with open(os.path.join(settings.BASE_DIR, 'object_inputs_and_default_values.json'), "r") as file:
        obj_inputs_and_default_values = json.load(file)

    response_objs, flat_obj_dict = json_to_system(request.session["system_data"])

    new_efootprint_obj_class = globals()[new_obj["obj_type"]]
    new_efootprint_obj = new_efootprint_obj_class.__new__(new_efootprint_obj_class)

    obj_creation_kwargs = {}
    obj_inputs = obj_inputs_and_default_values[new_obj["obj_type"]]

    obj_creation_kwargs["name"] = new_obj["name"]
    for attr_dict in obj_inputs["numerical_attributes"]:
        obj_creation_kwargs[attr_dict["attr_name"]] = SourceValue(
            float(new_obj[attr_dict["attr_name"]]) * u(attr_dict["unit"]))
    for mod_obj in obj_inputs["modeling_obj_attributes"]:
        obj_creation_kwargs[mod_obj["attr_name"]] = flat_obj_dict[new_obj[mod_obj["attr_name"]]]

    if new_obj["obj_type"] == "UsagePattern":
        obj_creation_kwargs["time_intervals"] = SourceObject([[7, 12], [18, 23]])

    new_efootprint_obj.__init__(**obj_creation_kwargs)

    response_objs[new_obj["obj_type"]][new_efootprint_obj.id] = new_efootprint_obj
    if new_obj["obj_type"] == "UsagePattern":
        for elt in response_objs["System"].values():
            system = elt
        system.usage_patterns += [new_efootprint_obj]
        request.session["system_data"]["System"][system.id]["usage_patterns"] = [up.id for up in system.usage_patterns]

    context = get_context_from_response_objs(response_objs)

    request.session["system_data"][new_obj["obj_type"]][new_efootprint_obj.id] = new_efootprint_obj.to_json()
    request.session.modified = True

    context["display_obj_form"] = "False"
    system_footprint_html = context["System"][0]["object"].plot_footprints_by_category_and_object()._repr_html_()

    return render(
        request, "model_builder/model-builder-main.html",
        context={"context": context, "systemFootprint": system_footprint_html})


def close_form(request):
    return render(request, "model_builder/object-creation-form.html", context={"display_obj_form": False})


def get_context_from_json(jsondata):
    response_objs, flat_obj_dict = json_to_system(jsondata)

    return get_context_from_response_objs(response_objs)


def get_context_from_response_objs(response_objs):
    obj_template_dict = {}
    for key, obj in response_objs.items():
        mod_obj_list = []
        for mod_obj_id, mod_obj in obj.items():
            mod_obj_list.append(
                {"object": mod_obj,
                 "numerical_attributes": [
                     attr_name_value_pair[1]
                     for attr_name_value_pair in retrieve_attributes_by_type(mod_obj, ExplainableQuantity)
                     if attr_name_value_pair[1].attr_name_in_mod_obj_container not in mod_obj.calculated_attributes],
                 "modeling_obj_attributes": [
                     attr_name_value_pair[1]
                     for attr_name_value_pair in retrieve_attributes_by_type(mod_obj, ModelingObject)],
                 "list_attributes": [
                     attr_name_value_pair[1]
                     for attr_name_value_pair in retrieve_attributes_by_type(mod_obj, list)]
                 }
            )
        obj_template_dict[key] = mod_obj_list

    return obj_template_dict


def retrieve_attributes_by_type(modeling_obj, attribute_type, attrs_to_ignore=['modeling_obj_containers']):
    output_list = []
    for attr_name, attr_value in vars(modeling_obj).items():
        if isinstance(attr_value, attribute_type) and attr_name not in attrs_to_ignore:
            output_list.append((attr_name, attr_value))

    return output_list
