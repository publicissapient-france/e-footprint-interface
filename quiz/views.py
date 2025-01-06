from datetime import datetime

from efootprint.api_utils.json_to_system import json_to_system
from efootprint.abstract_modeling_classes.source_objects import SourceValue
from efootprint.api_utils.system_to_json import system_to_json
from efootprint.builders.hardware.devices_defaults import default_laptop, default_smartphone
from efootprint.builders.hardware.servers_defaults import default_autoscaling
from efootprint.builders.hardware.storage_defaults import default_ssd
from efootprint.builders.time_builders import linear_growth_hourly_values, daily_fluct_hourly_values
from efootprint.constants.sources import Sources
from efootprint.core.hardware.servers.serverless import Serverless
from efootprint.constants.units import u
from efootprint.core.system import System
from efootprint.core.usage.job import Job
from efootprint.core.usage.usage_pattern import UsagePattern
from efootprint.core.usage.user_journey import UserJourney
from efootprint.core.usage.user_journey_step import UserJourneyStep
from efootprint.builders.hardware.network_defaults import default_mobile_network, default_wifi_network
from efootprint.constants.countries import Countries

from utils import htmx_render, EFOOTPRINT_COUNTRIES
from model_builder.views import model_builder_main

import json
from django.shortcuts import render


def onboarding(request):
    return htmx_render(request, "quiz/onboarding.html")


def user_journeys(request, error=None):
    user_journeys_steps = [""]

    return htmx_render(request, "quiz/user-journeys.html",
                       context={"user_journeys_steps": user_journeys_steps, "error": error})


def add_user_journey_step(request):
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
        return user_journeys(request, error="You must specify at least one user journey step")

    request.session['quiz_data'] = {'user_journey_steps': uj_steps}
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
    services_servers = {}
    services_storages = {}

    uj_steps = []

    for service_desc in request.session["quiz_data"]["services"]:
        if service_desc["type"] in ["web-app", "streaming"]:
            storage = default_ssd(f"Default {service_desc['type']} SSD storage")
            server = default_autoscaling(f"Default {service_desc['type']} autoscaling server" ,storage =storage)
        elif service_desc["type"] == "gen-ai":
            storage = default_ssd("Default SSD storage for AI server")
            server = Serverless(
                "Default AI GPU server",
                carbon_footprint_fabrication=SourceValue(4900 * u.kg, Sources.HYPOTHESIS),
                power=SourceValue(6400 * u.W, Sources.HYPOTHESIS),
                lifespan=SourceValue(5 * u.year, Sources.HYPOTHESIS),
                idle_power=SourceValue(500 * u.W, Sources.HYPOTHESIS),
                ram=SourceValue(128 * u.GB, Sources.HYPOTHESIS),
                cpu_cores=SourceValue(16 * u.core, Sources.HYPOTHESIS),
                # Used to represent GPUs because e-footprint doesn’t natively model GPU resources yet.
                power_usage_effectiveness=SourceValue(1.2 * u.dimensionless, Sources.HYPOTHESIS),
                average_carbon_intensity=SourceValue(300 * u.g / u.kWh, Sources.HYPOTHESIS),
                server_utilization_rate=SourceValue(1 * u.dimensionless, Sources.HYPOTHESIS),
                base_ram_consumption=SourceValue(0 * u.MB, Sources.HYPOTHESIS),
                base_cpu_consumption=SourceValue(0 * u.core, Sources.HYPOTHESIS),
                storage=storage
            )
            storage = default_ssd("Default SSD storage for AI server")

        services_servers[service_desc["type"]] = server
        services_storages[service_desc["type"]] = storage

    for service_desc in request.session["quiz_data"]["services"]:
        for uj_step_desc in request.session["quiz_data"]["user_journey_steps"]:
            if uj_step_desc["name"] in service_desc["called_by"]:
                uj_duration_in_min = float(uj_step_desc["duration_in_min"])
                if service_desc["type"] == "web-app":
                    job = Job(f"request {service_desc['type']} service",
                              server=services_servers[service_desc["type"]],
                              data_upload=SourceValue(0.05 * u.MB, Sources.USER_DATA),
                              data_download=SourceValue(2 * u.MB, Sources.USER_DATA),
                              data_stored=SourceValue(0.05 * u.MB, Sources.USER_DATA),
                              request_duration=SourceValue(1 * u.s, Sources.HYPOTHESIS),
                              cpu_needed=SourceValue(0.2 * u.core, Sources.HYPOTHESIS),
                              ram_needed=SourceValue(50 * u.MB, Sources.HYPOTHESIS))
                elif service_desc["type"] == "streaming":
                    job = Job(f"request {service_desc['type']} service",
                              server=services_servers[service_desc["type"]],
                              data_upload=SourceValue(0.05 * u.MB, Sources.USER_DATA),
                              data_download=SourceValue(40 * uj_duration_in_min * u.MB, Sources.USER_DATA),
                              data_stored=SourceValue(0.05 * u.MB, Sources.USER_DATA),
                              request_duration=SourceValue((uj_duration_in_min / 10) * u.min, Sources.HYPOTHESIS),
                              cpu_needed=SourceValue(0.2 * u.core, Sources.HYPOTHESIS),
                              ram_needed=SourceValue(50 * u.MB, Sources.HYPOTHESIS))
                elif service_desc["type"] == "gen-ai":
                    job = Job(f"request {service_desc['type']} service",
                              server=services_servers[service_desc["type"]],
                              data_upload=SourceValue(0.05 * u.MB, Sources.USER_DATA),
                              data_download=SourceValue(0.5 * u.MB, Sources.USER_DATA),
                              data_stored=SourceValue(0.05 * u.MB, Sources.USER_DATA),
                              request_duration=SourceValue((uj_duration_in_min / 20) * u.min, Sources.HYPOTHESIS),
                              cpu_needed=SourceValue(16 * u.core, Sources.HYPOTHESIS),
                              ram_needed=SourceValue(128 * u.GB, Sources.HYPOTHESIS))

                uj_step = UserJourneyStep(
                    uj_step_desc["name"],
                    user_time_spent=SourceValue(float(uj_step_desc["duration_in_min"]) * u.min, Sources.USER_DATA),
                    jobs=[job])

                uj_steps.append(uj_step)

    user_journey = UserJourney("My User Journey", uj_steps=uj_steps)

    if request.POST['device'] == "smartphone":
        network = default_mobile_network()
        device = default_smartphone()
    elif request.POST['device'] == "laptop":
        network = default_wifi_network()
        device = default_laptop()

    if len(request.POST['country']) == 0:
        return

    for attr_value in vars(Countries).values():
        if callable(attr_value):
            country = attr_value()
            if country.name == request.POST['country']:
                break

    start_date = datetime.strptime("2025-01-01", "%Y-%m-%d")
    nb_of_hours = 3 * u.year

    hourly_visits = int(int(request.POST['visitors']) / 24)
    linear_growth = linear_growth_hourly_values(
        nb_of_hours, start_value=hourly_visits, end_value=hourly_visits, start_date=start_date)
    linear_growth.set_label("Hourly user journeys linear growth component")
    daily_fluct = daily_fluct_hourly_values(nb_of_hours, fluct_scale=0.8, hour_of_day_for_min_value=4,
                                            start_date=start_date)
    daily_fluct.set_label("Daily volume fluctuation")
    hourly_user_journey_starts = linear_growth * daily_fluct
    hourly_user_journey_starts.set_label("Hourly number of user journey started")

    usage_pattern = UsagePattern(
        "Description of usage",
        user_journey=user_journey,
        country=country,
        devices=[device],
        network=network,
        hourly_user_journey_starts=hourly_user_journey_starts)

    system = System("System", usage_patterns=[usage_pattern])

    del request.session["quiz_data"]
    request.session["system_data"] = system_to_json(system, save_calculated_attributes=False)
    request.session["img_base64"] = None

    return model_builder_main(request)


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
