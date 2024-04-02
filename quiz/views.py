import json
from django.shortcuts import render
from efootprint.api_utils.json_to_system import json_to_system
from efootprint.abstract_modeling_classes.explainable_objects import ExplainableQuantity
from efootprint.abstract_modeling_classes.modeling_object import ModelingObject
from efootprint.utils.tools import convert_to_list


def home(request):
    return render(request, "home.html")


def understand(request):
    return render(request, "quiz/understand.html")


# Analyze views


def analyze_onboarding(request):
    return render(request, "quiz/analyze/onboarding.html")


def analyze_user_journeys(request):
    user_journeys_steps = [""]
    return render(request, "quiz/analyze/user-journeys.html", context={"user_journeys_steps": user_journeys_steps})


def add_user_journey_step(request):
    user_journeys_steps = []
    for key, obj in request.POST.items():
        user_journeys_steps.append(obj)
    user_journeys_steps.append("")
    return render(request, "quiz/analyze/user-journeys.html", context={"user_journeys_steps": user_journeys_steps})


def analyze_apis(request):
    return render(request, "quiz/analyze/apis.html")


def analyze_usage_patterns(request):
    return render(request, "quiz/analyze/usage-patterns.html")


def analyze(request):
    return render(request, "quiz/analyze/analyze.html")


def form(request):
    return render(request, "quiz/form.html")


def form_service(request):
    return render(request, "quiz/form-services.html")


def form_usage_pattern(request):
    return render(request, "quiz/form-usage-pattern.html")


def response(request):
    jsondata = json.loads(request.POST["json"])
    request.session["system_data"] = jsondata
    # compute calculated attributes with e-footprint
    context = get_context_from_json(jsondata)
    return render(request, "quiz/response.html", context={"context": context, "systemFootprint": context["System"][0]["object"].plot_footprints_by_category_and_object()._repr_html_()})


def update_value(request):
    request.session["system_data"][request.POST["key"]][request.POST["e-footprint-obj"]][request.POST["attr_name"]][
        "value"
    ] = float(request.POST[request.POST["e-footprint-obj"]])
    context = get_context_from_json(request.session["system_data"])
    return render(request, "quiz/graph-container.html", context={"context": context, "systemFootprint": context["System"][0]["object"].plot_footprints_by_category_and_object()._repr_html_()})


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
