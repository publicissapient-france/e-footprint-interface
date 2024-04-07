import json
from django.shortcuts import render
from efootprint.api_utils.json_to_system import json_to_system
from efootprint.abstract_modeling_classes.explainable_objects import ExplainableQuantity
from efootprint.abstract_modeling_classes.modeling_object import ModelingObject
from efootprint.utils.tools import convert_to_list


def analyze(request):
    return render(request, "analyze.html")


def form_usage_pattern(request):
    return render(request, "form-usage-pattern.html")


def response(request):
    jsondata = json.loads(request.POST["json"])
    request.session["system_data"] = jsondata
    # compute calculated attributes with e-footprint
    context = get_context_from_json(jsondata)
    system_footprint_html = context["System"][0]["object"].plot_footprints_by_category_and_object()._repr_html_()

    return render(
      request, "response.html", context={"context": context, "systemFootprint": system_footprint_html})


def update_value(request):
    object_type = request.POST["key"]
    object_name = request.POST["e-footprint-obj"]
    attr_name = request.POST["attr_name"]
    request.session["system_data"][object_type][object_name][attr_name]["value"] = float(request.POST["value"])
    context = get_context_from_json(request.session["system_data"])

    system_footprint_html = context["System"][0]["object"].plot_footprints_by_category_and_object()._repr_html_()

    return render(
      request, "graph-container.html", context={"context": context, "systemFootprint": system_footprint_html})


def add_service(request):
    print(request.session["system_data"]['Service'])
    return render(request, "response.html", context={"context": context, "systemFootprint": context["System"][0]["object"].plot_footprints_by_category_and_object()._repr_html_()})


def get_context_from_json(jsondata):
    response_objs, flat_obj_dict = json_to_system(jsondata)
    obj_template_dict = {}
    for key, obj in response_objs.items():
        mod_obj_list = []
        for mod_obj_id, mod_obj in obj.items():
            mod_obj_list.append(
                {"object": mod_obj,
                 "numerical_attributes" : [attr for attr in retrieve_attributes_by_type(mod_obj, ExplainableQuantity) if attr.attr_name_in_mod_obj_container not in mod_obj.calculated_attributes],
                 "modeling_obj_attributes" : retrieve_attributes_by_type(mod_obj, ModelingObject),
                 "list_attributes" : retrieve_attributes_by_type(mod_obj, list)
                 }
            )
        obj_template_dict[key] = mod_obj_list

    return obj_template_dict


def retrieve_attributes_by_type(modeling_obj, attribute_type):
    output_list = []
    for attr_name, attr_value in vars(modeling_obj).items():
        values = convert_to_list(attr_value)
        for value in values:
            if isinstance(value, attribute_type):
                output_list.append(value)

    return output_list
