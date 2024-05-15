from efootprint.api_utils.json_to_system import json_to_system
from efootprint.abstract_modeling_classes.explainable_objects import ExplainableQuantity
from efootprint.abstract_modeling_classes.modeling_object import ModelingObject, PREVIOUS_LIST_VALUE_SET_SUFFIX
from efootprint.api_utils.system_to_json import system_to_json
from efootprint.constants.units import u
from efootprint.core.usage.usage_pattern import UsagePattern
from efootprint.utils.plot_emission_diffs import EmissionPlotter
import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt

from model_builder.object_creation_utils import add_new_object_to_system, edit_object_in_system
from utils import htmx_render, EFOOTPRINT_COUNTRIES

from django.conf import settings
import json
from django.shortcuts import render
import os
from django.http import HttpResponse


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


def open_create_object_panel(request, object_type):
    with open(os.path.join(settings.BASE_DIR, 'object_inputs_and_default_values.json')) as object_inputs_file:
        object_inputs_and_default_values = json.load(object_inputs_file)

    modeling_obj_attributes, list_attributes = retrieve_existing_mod_obj_and_list_attributes(
        object_inputs_and_default_values, object_type, request)

    context_data = {
        "form_target_url": "add-new-object",
        "obj_type": object_type, "display_obj_form": True,
        "header": f"New {object_type}", "default_name": "",
        "numerical_attributes": object_inputs_and_default_values[object_type]["numerical_attributes"],
        "modeling_obj_attributes": modeling_obj_attributes,
        "list_attributes": list_attributes,
        "object_id": "",
        "output_button_label": "Save"
    }

    return render(request, "model_builder/object-creation-or-edition-form.html", context=context_data)


def open_edit_object_panel(request, object_type):
    with open(os.path.join(settings.BASE_DIR, 'object_inputs_and_default_values.json')) as object_inputs_file:
        object_inputs_and_default_values = json.load(object_inputs_file)

    modeling_obj_attributes, list_attributes = retrieve_existing_mod_obj_and_list_attributes(
        object_inputs_and_default_values, object_type, request)

    object_dict = request.session["system_data"][object_type][request.POST["object-id"]]
    for mod_obj_attribute_desc in modeling_obj_attributes:
        mod_obj_attribute_desc["selected"] = object_dict[mod_obj_attribute_desc["attr_name"]]

    for list_attributes_desc in list_attributes:
        list_attributes_desc["selected"] = object_dict[list_attributes_desc["attr_name"]]

    numerical_attributes = []
    for attr_key, attr_value in object_dict.items():
        if type(attr_value) == dict and "unit" in attr_value.keys():
            quantity = attr_value["value"] * u(attr_value["unit"])
            numerical_attributes.append(
                {"attr_name": attr_key, "unit": f"{quantity.units:~P}",
                 "long_unit": attr_value["unit"],
                 "default_value": attr_value["value"]}
            )

    context_data = {
        "form_target_url": "edit-object",
        "obj_type": object_type, "display_obj_form": True,
        "header": f"Editing {object_dict['name']}", "default_name": object_dict["name"],
        "numerical_attributes": numerical_attributes,
        "modeling_obj_attributes": modeling_obj_attributes,
        "list_attributes": list_attributes,
        "object_id": object_dict["id"],
        "output_button_label": "Edit",
    }

    return render(request, "model_builder/object-creation-or-edition-form.html", context=context_data)


def retrieve_existing_mod_obj_and_list_attributes(object_inputs_and_default_values, object_type, request):
    modeling_obj_attributes = object_inputs_and_default_values[object_type]["modeling_obj_attributes"]
    list_attributes = object_inputs_and_default_values[object_type]["list_attributes"]

    for mod_obj_attribute_desc in modeling_obj_attributes:
        # Retrieve existing objects of this type
        if mod_obj_attribute_desc["object_type"] == "Country":
            mod_obj_attribute_desc["existing_objects"] = [
                country.to_json() for country in EFOOTPRINT_COUNTRIES]
        else:
            mod_obj_attribute_desc["existing_objects"] = list(
                request.session["system_data"][mod_obj_attribute_desc["object_type"]].values())

    for list_attributes_desc in list_attributes:
        # Retrieve existing objects of this type
        list_attributes_desc["existing_objects"] = list(
            request.session["system_data"][list_attributes_desc["object_type"]].values())

    return modeling_obj_attributes, list_attributes


def add_new_object(request):
    response_objs, flat_obj_dict = json_to_system(request.session["system_data"])

    response_objs = add_new_object_to_system(request, response_objs, flat_obj_dict)

    context, system_footprint_html = get_context_from_response_objs(response_objs)

    is_ref_model_edited = request.session["system_data"] != request.session["reference_system_data"]

    return render(
        request, "model_builder/model-builder-main.html",
        context={"context": context, "systemFootprint": system_footprint_html, "display_obj_form": "False",
                 "is_ref_model_edited": is_ref_model_edited})


def edit_object(request):
    response_objs, flat_obj_dict = json_to_system(request.session["system_data"])

    response_objs = edit_object_in_system(request, response_objs, flat_obj_dict)

    context, system_footprint_html = get_context_from_response_objs(response_objs)

    is_ref_model_edited = request.session["system_data"] != request.session["reference_system_data"]

    return render(
        request, "model_builder/model-builder-main.html",
        context={"context": context, "systemFootprint": system_footprint_html, "display_obj_form": "False",
                 "is_ref_model_edited": is_ref_model_edited})


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

    is_ref_model_edited = request.session["system_data"] != request.session["reference_system_data"]

    context, system_footprint_html = get_context_from_response_objs(response_objs)

    return render(
        request, "model_builder/model-builder-main.html",
        context={"context": context, "systemFootprint": system_footprint_html, "display_obj_form": "False",
                 "is_ref_model_edited": is_ref_model_edited})


def get_context_from_json(jsondata):
    response_objs, flat_obj_dict = json_to_system(jsondata)

    return get_context_from_response_objs(response_objs)


def get_context_from_response_objs(response_objs):
    obj_template_dict = {}
    for key, obj in response_objs.items():
        if key not in ["System", "Country"]:
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


def download_json(request):
    data = request.session.get('system_data', {})
    json_data = json.dumps(data, indent=4)
    response = HttpResponse(json_data, content_type='application/json')
    response['Content-Disposition'] = f'attachment; filename="efootprint-model-system-data.json"'

    return response


def set_as_reference_model(request):
    request.session["reference_system_data"] = request.session["system_data"]
    print(request.session["reference_system_data"])
    return render(request, "model_builder/model-builder-main.html")


def compare_with_reference(request):
    ref_response_objs, ref_flat_obj_dict = json_to_system(request.session["reference_system_data"])
    response_objs, flat_obj_dict = json_to_system(request.session["system_data"])

    # for each system
    ref_system = list(ref_response_objs["System"].values())[0]
    system = list(response_objs["System"].values())[0]

    emissions_dict__old = [ref_system.initial_total_energy_footprints, ref_system.initial_total_fabrication_footprints]

    emissions_dict__new = [system.total_energy_footprints, system.total_fabrication_footprints]

    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(10, 5))

    EmissionPlotter(
        ax, emissions_dict__old, emissions_dict__new, rounding_value=1,
        timespan=ExplainableQuantity(1 * u.year, "one year")).plot_emission_diffs()

    from matplotlib.backends.backend_agg import FigureCanvasAgg
    import io
    import base64

    # Convert plot to binary buffer
    buf = io.BytesIO()
    canvas = FigureCanvasAgg(fig)
    canvas.print_png(buf)

    # Encode binary buffer as base64
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode()

    # Close plot to free memory
    plt.close(fig)

    return render(request, 'model_builder/compare-container.html', {'img_base64': img_base64})
