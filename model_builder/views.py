from efootprint.api_utils.json_to_system import json_to_system
from efootprint.abstract_modeling_classes.explainable_objects import ExplainableQuantity
from efootprint.abstract_modeling_classes.modeling_object import ModelingObject, PREVIOUS_LIST_VALUE_SET_SUFFIX
from model_builder.object_creation_utils import create_efootprint_obj_from_post_data
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
    with open(os.path.join(settings.BASE_DIR, 'object_inputs_and_default_values.json')) as object_inputs_file:
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
    response_objs, flat_obj_dict = json_to_system(request.session["system_data"])
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
    context = get_context_from_response_objs(response_objs)

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
            list_attributes = retrieve_attributes_by_type(mod_obj, list)
            if len(list_attributes) > 0:
                list_attributes = list_attributes[0][1]
            mod_obj_list.append(
                {"object": mod_obj,
                 "numerical_attributes": [
                     attr_name_value_pair[1]
                     for attr_name_value_pair in retrieve_attributes_by_type(mod_obj, ExplainableQuantity)
                     if attr_name_value_pair[1].attr_name_in_mod_obj_container not in mod_obj.calculated_attributes],
                 "modeling_obj_attributes": [
                     attr_name_value_pair[1]
                     for attr_name_value_pair in retrieve_attributes_by_type(mod_obj, ModelingObject)],
                 "list_attributes": list_attributes
                 }
            )
        obj_template_dict[key] = mod_obj_list

    return obj_template_dict


def retrieve_attributes_by_type(modeling_obj, attribute_type, attrs_to_ignore=['modeling_obj_containers']):
    output_list = []
    for attr_name, attr_value in vars(modeling_obj).items():
        if isinstance(attr_value, attribute_type) and attr_name not in attrs_to_ignore and PREVIOUS_LIST_VALUE_SET_SUFFIX not in attr_name:
            output_list.append((attr_name, attr_value))

    return output_list
