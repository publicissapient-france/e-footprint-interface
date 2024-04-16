from efootprint.api_utils.json_to_system import json_to_system
from efootprint.abstract_modeling_classes.explainable_objects import ExplainableQuantity
from efootprint.abstract_modeling_classes.modeling_object import ModelingObject, PREVIOUS_LIST_VALUE_SET_SUFFIX
from efootprint.api_utils.system_to_json import system_to_json
from efootprint.constants.units import u
from efootprint.core.usage.usage_pattern import UsagePattern

from model_builder.object_creation_utils import add_new_object_to_system, edit_object_in_system
from utils import htmx_render

from django.conf import settings
import json
from django.shortcuts import render
import os


def model_builder_main(request):
    try:
        jsondata = request.session["system_data"]
    except KeyError:
        with open(os.path.join("model_builder", "default_system_data.json"), "r") as file:
            jsondata = json.load(file)
            request.session["system_data"] = jsondata

    # compute calculated attributes with e-footprint
    context, system_footprint_html = get_context_from_json(jsondata)

    return htmx_render(
        request, "model_builder/model-builder-main.html",
        context={"context": context, "systemFootprint": system_footprint_html})


def update_value(request):
    object_type = request.POST["key"]
    object_name = request.POST["e-footprint-obj"]
    attr_name = request.POST["attr_name"]
    request.session["system_data"][object_type][object_name][attr_name]["value"] = float(request.POST["value"])
    request.session.modified = True
    context, system_footprint_html = get_context_from_json(request.session["system_data"])

    return render(
        request, "model_builder/graph-container.html",
        context={"context": context, "systemFootprint": system_footprint_html})


def open_object_panel(request):
    object_type = request.POST["object-type"]
    with open(os.path.join(settings.BASE_DIR, 'object_inputs_and_default_values.json')) as object_inputs_file:
        object_inputs_and_default_values = json.load(object_inputs_file)

    modeling_obj_attributes = object_inputs_and_default_values[object_type]["modeling_obj_attributes"]
    list_attributes = object_inputs_and_default_values[object_type]["list_attributes"]

    for mod_obj_attribute_desc in modeling_obj_attributes:
        # Retrieve existing objects of this type
        mod_obj_attribute_desc["existing_objects"] = list(
            request.session["system_data"][mod_obj_attribute_desc["object_type"]].values())

    for list_attributes_desc in list_attributes:
        # Retrieve existing objects of this type
        list_attributes_desc["existing_objects"] = list(
            request.session["system_data"][list_attributes_desc["object_type"]].values())

    is_an_object_edition = False
    header = f"New {object_type}"
    default_name = ""
    object_id = ""
    if "object-id" not in request.POST.keys():
        numerical_attributes = object_inputs_and_default_values[object_type]["numerical_attributes"]
    else:
        is_an_object_edition = True
        object_dict = request.session["system_data"][object_type][request.POST["object-id"]]
        header = f"Editing {object_dict['name']}"
        default_name = object_dict["name"]
        object_id = object_dict["id"]
        numerical_attributes = []
        for attr_key, attr_value in object_dict.items():
            if type(attr_value) == dict and "unit" in attr_value.keys():
                quantity = attr_value["value"] * u(attr_value["unit"])
                numerical_attributes.append(
                    {"attr_name": attr_key, "unit": f"{quantity.units:~P}",
                     "long_unit": attr_value["unit"],
                     "default_value": attr_value["value"]}
                )

        for mod_obj_attribute_desc in modeling_obj_attributes:
            mod_obj_attribute_desc["selected"] = object_dict[mod_obj_attribute_desc["attr_name"]]

        for list_attributes_desc in list_attributes:
            list_attributes_desc["selected"] = object_dict[list_attributes_desc["attr_name"]]

    context_data = {
        "is_an_object_edition": is_an_object_edition,
        "obj_type": object_type, "display_obj_form": True,
        "header": header, "default_name": default_name,
        "numerical_attributes": numerical_attributes,
        "modeling_obj_attributes": modeling_obj_attributes,
        "list_attributes": list_attributes,
        "object_id": object_id
    }

    return render(request, "model_builder/object-creation-form.html", context=context_data)


def add_new_object(request):
    response_objs, flat_obj_dict = json_to_system(request.session["system_data"])

    if request.POST["is_an_object_edition"] == "False":
        response_objs = add_new_object_to_system(request, response_objs, flat_obj_dict)
    else:
        response_objs = edit_object_in_system(request, response_objs, flat_obj_dict)

    context, system_footprint_html = get_context_from_response_objs(response_objs)

    return render(
        request, "model_builder/model-builder-main.html",
        context={"context": context, "systemFootprint": system_footprint_html, "display_obj_form": "False"})


def delete_object(request):
    response_objs, flat_obj_dict = json_to_system(request.session["system_data"])

    obj_id = request.POST["object-id"]
    obj_type = request.POST["object-type"]

    if obj_type == "UsagePattern":
        system = list(response_objs["System"].values())[0]
        system.usage_patterns = [up for up in system.usage_patterns if up.id != obj_id]

    flat_obj_dict[obj_id].self_delete()
    response_objs[obj_type].pop(obj_id, None)
    flat_obj_dict.pop(obj_id, None)

    request.session["system_data"] = system_to_json(
        list(response_objs["System"].values())[0], save_calculated_attributes=False)

    context, system_footprint_html = get_context_from_response_objs(response_objs)

    return render(
        request, "model_builder/model-builder-main.html",
        context={"context": context, "systemFootprint": system_footprint_html, "display_obj_form": "False"})


def close_form(request):
    return render(request, "model_builder/object-creation-form.html", context={"display_obj_form": False})


def get_context_from_json(jsondata):
    response_objs, flat_obj_dict = json_to_system(jsondata)

    return get_context_from_response_objs(response_objs)


def get_context_from_response_objs(response_objs):
    obj_template_dict = {}
    for key, obj in response_objs.items():
        if key != "System":
            mod_obj_list = []
            for mod_obj in obj.values():
                list_attributes = retrieve_attributes_by_type(mod_obj, list)
                if len(list_attributes) > 0:
                    list_attributes = list_attributes[0][1]
                is_deletable = False
                if not mod_obj.modeling_obj_containers:
                    is_deletable = True
                system = list(response_objs["System"].values())[0]
                if isinstance(mod_obj, UsagePattern) and len(system.usage_patterns) > 1:
                    is_deletable = True
                mod_obj_dict = {
                    "object": mod_obj,
                    "numerical_attributes": [
                         attr_name_value_pair[1]
                         for attr_name_value_pair in retrieve_attributes_by_type(mod_obj, ExplainableQuantity)
                         if attr_name_value_pair[1].attr_name_in_mod_obj_container not in mod_obj.calculated_attributes
                     ],
                    "modeling_obj_attributes": [
                         attr_name_value_pair[1]
                         for attr_name_value_pair in retrieve_attributes_by_type(mod_obj, ModelingObject)],
                    "list_attributes": list_attributes,
                    "is_deletable": is_deletable
                }
                for num_attr in mod_obj_dict["numerical_attributes"]:
                    num_attr.short_unit = f"{num_attr.value.units:~P}"
                    num_attr.readable_attr_name = num_attr.attr_name_in_mod_obj_container.replace("_", " ")
                mod_obj_list.append(mod_obj_dict)
            obj_template_dict[key] = mod_obj_list

    system = list(response_objs["System"].values())[0]
    system_footprint_html = system.plot_footprints_by_category_and_object()._repr_html_()

    return obj_template_dict, system_footprint_html


def retrieve_attributes_by_type(modeling_obj, attribute_type, attrs_to_ignore=['modeling_obj_containers']):
    output_list = []
    for attr_name, attr_value in vars(modeling_obj).items():
        if isinstance(attr_value, attribute_type) and attr_name not in attrs_to_ignore and PREVIOUS_LIST_VALUE_SET_SUFFIX not in attr_name:
            output_list.append((attr_name, attr_value))

    return output_list
