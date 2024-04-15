from utils import htmx_render

from django.shortcuts import render
from efootprint.constants.countries import Countries
from model_builder.views import model_builder_main


def onboarding(request):
    return htmx_render(request, "quiz/onboarding.html")


def user_journeys(request):
    user_journeys_steps = [""]

    return htmx_render(request, "quiz/user-journeys.html", context={"user_journeys_steps": user_journeys_steps})


def add_user_journey_step(request):
    latest_index = int(request.POST['latestIndex'])

    return render(request, "quiz/components/uj-input.html", context={"number": latest_index + 1})


def services(request):
    uj_steps = []
    for key in request.POST.keys():
        uj_step = request.POST.getlist(key)
        if uj_step[0] != '' and uj_step[1]:
            uj_steps.append({"name": uj_step[0], "duration_in_min": uj_step[1]})

    request.session['quiz_data'] = {'user_journey_steps': uj_steps}
    request.session.modified = True

    return htmx_render(request, "quiz/services.html",
                       context={"uj_steps": uj_steps})


def form_usage_pattern(request):
    services_list = []
    services_dict = {}
    for key in request.POST.keys():
        service = request.POST.getlist(key)
        if service[1] not in services_dict.keys():
            services_dict[service[1]] = [service[0]]
        else:
            services_dict[service[1]].append(service[0])
    for key in services_dict:
        services_list.append({"type": key, "called_by": services_dict[key]})
    request.session['quiz_data']['services'] = services_list
    request.session.modified = True
    countries_list = []
    for attr_value in vars(Countries).values():
        if callable(attr_value):
            countries_list.append(attr_value())
    return htmx_render(request, "quiz/usage-patterns.html", context={"countries": countries_list})


def analyze(request):
    request.session['quiz_data']['usage_pattern'] = {
        "device_type": request.POST['device'],
        "population_size": request.POST['visitors'],
        "country": request.POST['country']
    }
    request.session.modified = True
    print(request.session['quiz_data'])
    return model_builder_main(request)
