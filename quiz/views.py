import json
from django.shortcuts import render
from efootprint.api_utils.json_to_system import json_to_system


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
    return render(request, "quiz/response.html", context=context)


def update_value(request):
    request.session["system_data"][request.POST["key"]][request.POST["e-footprint-obj"]][request.POST["attr_name"]][
        "value"
    ] = float(request.POST[request.POST["e-footprint-obj"]])
    context = get_context_from_json(request.session["system_data"])
    return render(request, "quiz/graph-container.html", context=context)


def get_context_from_json(jsondata):
    response_objs, flat_obj_dict = json_to_system(jsondata)

    usage_patterns = [response_objs["UsagePattern"][key] for key in list(response_objs["UsagePattern"].keys())]
    user_journeys = [pattern.user_journey for pattern in usage_patterns]
    services = [response_objs["Service"][key] for key in list(response_objs["Service"].keys())]

    for key, obj in response_objs["System"].items():
        system = obj
    system_footprint = system.plot_footprints_by_category_and_object("System footprints.html")
    return {
        "systemFootprint": system_footprint._repr_html_(),
        "usagePatterns": usage_patterns,
        "userJourneys": user_journeys,
        "services": services,
    }
