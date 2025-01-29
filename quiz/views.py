import json
from django.shortcuts import render

from efootprint.api_utils.json_to_system import json_to_system

from utils import htmx_render, EFOOTPRINT_COUNTRIES
from model_builder.views import model_builder_main


def onboarding(request):
    return htmx_render(request, "quiz/onboarding.html")


def usage_journeys(request, error=None):
    usage_journeys_steps = [""]

    return htmx_render(request, "quiz/user-journeys.html",
                       context={"usage_journeys_steps": usage_journeys_steps, "error": error})


def add_usage_journey_step(request):
    latest_index = int(request.POST['latestIndex'])

    return render(request, "quiz/components/uj-input.html", context={"number": latest_index})


def services(request):
    uj_steps = []
    nb_steps = int(len(request.POST) / 2)
    for step in range(1, nb_steps + 1):
        uj_steps.append({
            "name": request.POST[f"step-desc-{step}"],
            "duration_in_min": request.POST[f"step-duration-{step}"],
        })

    if len(uj_steps) < 1:
        return usage_journeys(request, error="You must specify at least one usage journey step")

    request.session['quiz_data'] = {'usage_journey_steps': uj_steps}
    request.session.modified = True

    return htmx_render(request, "quiz/services.html",
                       context={"uj_steps": uj_steps})


def form_usage_pattern(request):
    services_list = []
    services_dict = {}

    nb_steps = int(len(request.POST) / 2)
    for step in range(1, nb_steps + 1):
        services_list.append({
            "type": request.POST[f"service-step-{step}"],
            "called_by": request.POST[f"step-{step}"]
        })

    request.session['quiz_data']['services'] = services_list
    request.session.modified = True

    return htmx_render(request, "quiz/usage-patterns.html", context={"countries": EFOOTPRINT_COUNTRIES})


def analyze(request):
    raise NotImplementedError("This view is deprecated and will probably be removed in the future")


def import_json(request):
    if "import-json-input" in request.FILES:
        try:
            file = request.FILES['import-json-input']
            if file and file.name.lower().endswith('.json'):
                data = json.load(file)
            else:
                return htmx_render(request, "quiz/onboarding.html",
                                   context={"uploadError": "Invalid file format ! Please use a JSON file"})
        except ValueError:
            return htmx_render(request, "quiz/onboarding.html", context={"uploadError": "Invalid JSON data"})
        try:
            json_to_system(data)
            request.session["system_data"] = data
            request.session["empty_objects"] = {}
            response = model_builder_main(request)
            response.headers = {"HX-Push-Url": "/model_builder/"}
            return response
        except Exception:
            return htmx_render(
                request, "quiz/onboarding.html", context={
                    "uploadError": f"Not a valid e-footprint model ! Please only input files generated by e-footprint"
                                   f" or the interface"})

    return htmx_render(request, "quiz/onboarding.html", context={"uploadError": "No file uploaded"})
