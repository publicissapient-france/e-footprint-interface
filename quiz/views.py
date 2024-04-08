from utils import htmx_render

from django.shortcuts import render


def onboarding(request):
    return htmx_render(request, "quiz/onboarding.html")


def user_journeys(request):
    user_journeys_steps = [""]

    return htmx_render(request, "quiz/user-journeys.html", context={"user_journeys_steps": user_journeys_steps})


def add_user_journey_step(request):
    latest_index = int(request.POST['latestIndex'])

    return render(request, "quiz/components/uj-input.html", context={"number": latest_index + 1})


def apis(request):
    return htmx_render(request, "quiz/apis.html")


def usage_patterns(request):
    return htmx_render(request, "quiz/usage-patterns.html")


def form(request):
    return render(request, "quiz/form.html")


def services(request):
    uj_steps = []
    for value in request.POST.values():
        if value != '':
            uj_steps.append({"name": value})

    request.session['quiz_data'] = {'user_journey_steps': uj_steps}

    print(request.session['quiz_data']['user_journey_steps'])
    return render(request, "quiz/form-services.html")


def form_usage_pattern(request):
    return htmx_render(request, "quiz/form-usage-pattern.html")


def add_step(request):
    latest_index = int(request.POST['latestIndex'])

    return render(request, "quiz/components/uj-input.html", context={"number": latest_index + 1})
