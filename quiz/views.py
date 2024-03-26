import json
from django.shortcuts import render
from efootprint.api_utils.json_to_system import json_to_system

def home(request):
    return render(request, "home.html")

def form(request):
    return render(request, "quiz/form.html")


def form_service(request):
    return render(request, "quiz/form-services.html")

def form_usage_pattern(request):
    return render(request, "quiz/form-usage-pattern.html")

def analyze(request):
    return render(request, "quiz/analyze.html")

def response(request):
    jsondata = json.loads(request.POST['json'])
    request.session["system_data"] = jsondata
    # compute calculated attributes with e-footprint
    context = get_context_from_json(jsondata)
    return render(request, "quiz/response.html", context=context)

def update_value(request):
    request.session["system_data"]["UserJourneyStep"][request.POST["e-footprint-obj"]][request.POST["attr_name"]]['value'] = float(request.POST[request.POST["e-footprint-obj"]])
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
    return {"systemFootprint": system_footprint._repr_html_(),"usagePatterns": usage_patterns, "userJourneys": user_journeys, "services": services}
