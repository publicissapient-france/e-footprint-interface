from efootprint.api_utils.json_to_system import json_to_system
from efootprint.abstract_modeling_classes.source_objects import SourceValue, SourceObject
from efootprint.api_utils.system_to_json import system_to_json
from efootprint.builders.hardware.devices_defaults import default_laptop, default_smartphone
from efootprint.builders.hardware.servers_defaults import default_autoscaling
from efootprint.builders.hardware.storage_defaults import default_ssd
from efootprint.constants.sources import Sources
from efootprint.core.hardware.device_population import DevicePopulation
from efootprint.core.hardware.servers.autoscaling import Autoscaling
from efootprint.core.service import Service
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

    return htmx_render(request, "quiz/usage-patterns.html", context={"countries": EFOOTPRINT_COUNTRIES})


def analyze(request):
    efootprint_services = {}
    uj_steps = []

    for service_desc in request.session["quiz_data"]["services"]:
        if service_desc["type"] in ["web-app", "streaming"]:
            server = default_autoscaling(f"Default {service_desc['type']} autoscaling server")
            storage = default_ssd(f"Default {service_desc['type']} SSD storage")
            service = Service(
                f"{service_desc['type']} service",
                server=server,
                storage=storage,
                base_ram_consumption=SourceValue(300 * u.MB, Sources.HYPOTHESIS),
                base_cpu_consumption=SourceValue(2 * u.core, Sources.HYPOTHESIS))
        elif service_desc["type"] == "gen-ai":
            llm_server = Autoscaling(
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
                server_utilization_rate=SourceValue(1 * u.dimensionless, Sources.HYPOTHESIS))
            storage = default_ssd("Default SSD storage for AI server")
            service = Service(
                f"{service_desc['type']} service", llm_server, storage,
                base_ram_consumption=SourceValue(0 * u.MB, Sources.HYPOTHESIS),
                base_cpu_consumption=SourceValue(0 * u.core, Sources.HYPOTHESIS))
        efootprint_services[service_desc["type"]] = service

    for service_desc in request.session["quiz_data"]["services"]:
        for uj_step_desc in request.session["quiz_data"]["user_journey_steps"]:
            if uj_step_desc["name"] in service_desc["called_by"]:
                uj_duration_in_min = float(uj_step_desc["duration_in_min"])
                if service_desc["type"] == "web-app":
                    job = Job(f"request {service_desc['type']} service",
                              service=efootprint_services[service_desc["type"]],
                              data_upload=SourceValue(0.05 * u.MB / u.uj, Sources.USER_DATA),
                              data_download=SourceValue(2 * u.MB / u.uj, Sources.USER_DATA),
                              request_duration=SourceValue(1 * u.s, Sources.HYPOTHESIS),
                              cpu_needed=SourceValue(0.2 * u.core / u.uj, Sources.HYPOTHESIS),
                              ram_needed=SourceValue(50 * u.MB / u.uj, Sources.HYPOTHESIS))
                elif service_desc["type"] == "streaming":
                    job = Job(f"request {service_desc['type']} service",
                              service=efootprint_services[service_desc["type"]],
                              data_upload=SourceValue(0.05 * u.MB / u.uj, Sources.USER_DATA),
                              data_download=SourceValue(40 * uj_duration_in_min * u.MB / u.uj, Sources.USER_DATA),
                              request_duration=SourceValue((uj_duration_in_min / 10) * u.min, Sources.HYPOTHESIS),
                              cpu_needed=SourceValue(0.2 * u.core / u.uj, Sources.HYPOTHESIS),
                              ram_needed=SourceValue(50 * u.MB / u.uj, Sources.HYPOTHESIS))
                elif service_desc["type"] == "gen-ai":
                    job = Job(f"request {service_desc['type']} service",
                              service=efootprint_services[service_desc["type"]],
                              data_upload=SourceValue(0.05 * u.MB / u.uj, Sources.USER_DATA),
                              data_download=SourceValue(0.5 * u.MB / u.uj, Sources.USER_DATA),
                              request_duration=SourceValue((uj_duration_in_min / 20) * u.min, Sources.HYPOTHESIS),
                              cpu_needed=SourceValue(16 * u.core / u.uj, Sources.HYPOTHESIS),
                              ram_needed=SourceValue(128 * u.GB / u.uj, Sources.HYPOTHESIS))

                uj_step = UserJourneyStep(
                    uj_step_desc["name"],
                    user_time_spent=SourceValue(float(uj_step_desc["duration_in_min"]) * u.min / u.uj, Sources.USER_DATA),
                    jobs=[job])

                uj_steps.append(uj_step)

    user_journey = UserJourney("My User Journey", uj_steps=uj_steps)

    if request.POST['device'] == "smartphone":
        network = default_mobile_network()
        device = default_smartphone()
    elif request.POST['device'] == "laptop":
        network = default_wifi_network()
        device = default_laptop()

    for attr_value in vars(Countries).values():
        if callable(attr_value):
            country = attr_value()
            if country.name == request.POST['country']:
                break

    device_population = DevicePopulation(
        "Device population",
        nb_devices=SourceValue(int(request.POST['visitors']) * u.user, Sources.USER_DATA),
        country=country,
        devices=[device])

    usage_pattern = UsagePattern(
        "Description of usage",
        user_journey=user_journey,
        device_population=device_population,
        network=network,
        user_journey_freq_per_user=SourceValue(1 * u.user_journey / (u.user * u.day), Sources.USER_DATA),
        time_intervals=SourceObject([[7, 12], [17, 23]]))

    system = System("System", usage_patterns=[usage_pattern])

    del request.session["quiz_data"]

    request.session["system_data"] = system_to_json(system, save_calculated_attributes=False)

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
            response = model_builder_main(request)
            request.session["system_data"] = data
            response.headers = {"HX-Push-Url": "/model_builder/"}
            return response
        except Exception:
            return htmx_render(
                request, "quiz/onboarding.html", context={
                    "uploadError": f"Not a valid e-footprint model ! Please only input files generated by e-footprint"
                                   f" or the interface"})

    return htmx_render(request, "quiz/onboarding.html", context={"uploadError": "No file uploaded"})

