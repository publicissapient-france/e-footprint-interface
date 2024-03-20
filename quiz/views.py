import json
from django.shortcuts import render
from efootprint.api_utils.json_to_system import json_to_system

def home(request):
    return render(request, "home.html")

def quiz(request):
    return render(request, "quiz/quiz.html")

def form(request):
    return render(request, "quiz/form.html")


def form_service(request):
    return render(request, "quiz/form-services.html")

def form_usage_pattern(request):
    return render(request, "quiz/form-usage-pattern.html")

def response(request):
    jsondata = json.loads(request.POST['json'])
    # compute calculated attributes with e-footprint
    response_objs, flat_obj_dict = json_to_system(jsondata)

    usage_patterns = [response_objs["UsagePattern"][key] for key in list(response_objs["UsagePattern"].keys())]

    user_journeys = [pattern.user_journey for pattern in usage_patterns]

    services = [response_objs["Service"][key] for key in list(response_objs["Service"].keys())]

    return render(request, "quiz/response.html", context={"usagePatterns": usage_patterns, "userJourneys": user_journeys, "services": services})
