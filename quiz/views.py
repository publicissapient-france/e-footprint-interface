import json
from django.shortcuts import render

def home(request):
    return render(request, "home.html")

def understand(request):
    return render(request, "understand.html")

def onboarding(request):
    return render(request, "onboarding.html")

def user_journeys(request):
    user_journeys_steps = [""]
    return render(request, "user-journeys.html", context={"user_journeys_steps": user_journeys_steps})

def add_user_journey_step(request):
    user_journeys_steps = []
    for key, obj in request.POST.items():
        user_journeys_steps.append(obj)
    user_journeys_steps.append("")
    return render(request, "user-journeys.html", context={"user_journeys_steps": user_journeys_steps})

def apis(request):
    return render(request, "apis.html")


def usage_patterns(request):
    return render(request, "usage-patterns.html")

def form(request):
    return render(request, "form.html")

def form_service(request):
    uj_steps = []
    for value in request.POST.values():
        if value != '':
            uj_steps.append({"name": value})

    request.session['quiz_data'] = {'user_journey_steps': uj_steps}

    print(request.session['quiz_data']['user_journey_steps'])
    return render(request, "quiz/form-services.html")

def form_usage_pattern(request):
    return render(request, "form-usage-pattern.html")

def add_step(request):
    latest_index = int(request.POST['latestIndex'])

    return render(request, "components/uj-input.html", context={"number": latest_index + 1})

