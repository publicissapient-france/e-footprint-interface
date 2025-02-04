import json

from efootprint.abstract_modeling_classes.source_objects import SourceValue
from efootprint.constants.units import u
from efootprint.core.all_classes_in_order import SERVER_CLASSES, SERVICE_CLASSES, SERVER_BUILDER_CLASSES
from efootprint.core.hardware.storage import Storage
from django.shortcuts import render
from efootprint.core.usage.job import Job
from efootprint.core.usage.usage_journey_step import UsageJourneyStep

from model_builder.class_structure import generate_object_creation_structure, efootprint_class_structure
from model_builder.model_web import ModelWeb, DEFAULT_NETWORKS, DEFAULT_COUNTRIES, DEFAULT_HARDWARES
from model_builder.object_creation_and_edition_utils import create_efootprint_obj_from_post_data, \
    add_new_efootprint_object_to_system, render_exception_modal
from model_builder.views_edition import edit_object


def open_create_object_panel(request, object_type):
    new_object_structure = efootprint_class_structure(object_type, ModelWeb(request.session))
    assert object_type in ["UsageJourney", "UsageJourneyStep"]
    template_name_mapping = {
        "UsageJourney": "usage_journey", "UsageJourneyStep": "usage_journey_step"}
    template_name = template_name_mapping[object_type]
    context_data = {"object_structure": new_object_structure,
                    "header_name": "Create " +  template_name.replace("_", " "),
                    "new_object_name": "New " + template_name.replace("_", " ")}
    if request.GET.get('efootprint_id_of_parent_to_link_to'):
        context_data['efootprint_id_of_parent_to_link_to'] = request.GET['efootprint_id_of_parent_to_link_to']
    if request.GET.get("name"):
        context_data["new_object_name"] = request.GET["name"]

    return render(request, f"model_builder/side_panels/{template_name}_add.html", context=context_data)


def open_create_server_panel(request):
    structure_dict, dynamic_form_data = generate_object_creation_structure(
        SERVER_CLASSES + SERVER_BUILDER_CLASSES, "Server type", ["fixed_nb_of_instances"])

    http_response = render(request, f"model_builder/side_panels/server_add.html",
                  context={'structure_dict': structure_dict, "dynamic_form_data": dynamic_form_data,
                           "obj_type": "server"})

    http_response["HX-Trigger-After-Swap"] = "initAddPanel"

    return http_response


def open_create_service_panel(request, server_efootprint_id):
    model_web = ModelWeb(request.session)
    server = model_web.get_web_object_from_efootprint_id(server_efootprint_id)

    installable_services = server.installable_services()
    services_dict, dynamic_form_data = generate_object_creation_structure(
        installable_services, "Services available for this server", ["gpu_latency_alpha", "gpu_latency_beta"])

    http_response = render(
        request, "model_builder/side_panels/service_add.html", {
            "server_id": server_efootprint_id, "structure_dict": services_dict, "dynamic_form_data": dynamic_form_data,
            "obj_type": "service"})

    http_response["HX-Trigger-After-Swap"] = "initAddPanel"

    return http_response

def open_create_job_panel(request):
    model_web = ModelWeb(request.session)
    servers = model_web.servers

    available_job_classes = {Job}
    for service in SERVICE_CLASSES:
        if service.__name__ in request.session["system_data"].keys():
            available_job_classes.update(service.compatible_jobs())

    structure_dict, dynamic_form_data = generate_object_creation_structure(list(available_job_classes), "Job type")
    additional_item = {
                "category": "job_creation_helper",
                "header": "Job creation helper",
                "class": "",
                "fields": [
                    {
                        "input_type": "select",
                        "id": "server",
                        "name": "Server",
                        "options": [
                            {'label': server.name, 'value': server.efootprint_id} for server in servers]
                    },
                    {
                        "input_type": "select",
                        "id": "service",
                        "name": "Service used",
                        "options": None
                    },
                ]
            }
    structure_dict["items"] = [additional_item] + structure_dict["items"]

    possible_job_types_per_service = {"direct_server_call": [{"label": "Manually defined job", "value": "Job"}]}
    possible_job_types_per_service.update({
        service.efootprint_id: [
            {"label": job.__name__, "value": job.__name__} for job in service.compatible_jobs()]
        for service in model_web.services}
    )
    dynamic_form_data["dynamic_selects"] = [
        {
            "input": "service",
            "filter_by": "server",
            "list_value": {
                server.efootprint_id:
                    [{"label": "direct call to server", "value": "direct_server_call"}]
                    + [{"label": service.name, "value": service.efootprint_id}
                       for service in server.installed_services] for server in servers
            }
        },
        {
            "input": "type_object_available",
            "filter_by": "service",
            "list_value": possible_job_types_per_service
        }]

    http_response = render(
        request, "model_builder/side_panels/job_add.html", {
            "structure_dict": structure_dict, "dynamic_form_data": dynamic_form_data, "obj_type": "job",
            "efootprint_id_of_parent_to_link_to": request.GET.get('efootprint_id_of_parent_to_link_to')
        })
    http_response["HX-Trigger-After-Swap"] = "initAddPanel"

    return http_response

def open_create_usage_pattern_panel(request):
    model_web = ModelWeb(request.session)
    networks = [{"efootprint_id": network["id"], "name": network["name"]} for network in DEFAULT_NETWORKS.values()]
    countries = [{"efootprint_id": country["id"], "name": country["name"]} for country in DEFAULT_COUNTRIES.values()]
    devices = [{"efootprint_id": device["id"], "name": device["name"]} for device in DEFAULT_HARDWARES.values()]

    http_response = render(
        request, "model_builder/side_panels/usage_pattern_add.html", {
            "usageJourneys": model_web.usage_journeys,
            "networks": networks,
            "countries": countries,
            "devices": devices
        })

    return http_response


def add_new_usage_journey(request):
    model_web = ModelWeb(request.session)

    if not request.POST.getlist("uj_steps"):
        mutable_post = request.POST.copy()
        new_uj_step = UsageJourneyStep("Default usage journey step", SourceValue(1 * u.min), jobs=[])
        add_new_efootprint_object_to_system(request.session, model_web, new_uj_step)
        mutable_post.setlist('uj_steps', [new_uj_step.id])
        request.POST = mutable_post

    new_efootprint_obj = create_efootprint_obj_from_post_data(request, model_web, 'UsageJourney')
    added_obj = add_new_efootprint_object_to_system(request.session, model_web, new_efootprint_obj)
    response = render(
        request, "model_builder/object_cards/usage_journey_card.html", {"usage_journey": added_obj})
    response["HX-Trigger-After-Swap"] = json.dumps({
        "updateTopParentLines": {"topParentIds": [added_obj.web_id]},
        "setAccordionListeners": {"accordionIds": [added_obj.web_id]},
        "closePanelAfterSwap": True
    })

    return response


def add_new_usage_journey_step(request, usage_journey_efootprint_id):
    model_web = ModelWeb(request.session)
    new_efootprint_obj = create_efootprint_obj_from_post_data(request, model_web, 'UsageJourneyStep')
    added_obj = add_new_efootprint_object_to_system(request.session, model_web, new_efootprint_obj)
    usage_journey_to_edit = model_web.get_web_object_from_efootprint_id(usage_journey_efootprint_id)
    mutable_post = request.POST.copy()
    mutable_post['name'] = usage_journey_to_edit.name
    usage_journey_step_ids = [uj_step.efootprint_id for uj_step in usage_journey_to_edit.uj_steps]
    usage_journey_step_ids.append(added_obj.efootprint_id)
    mutable_post.setlist('uj_steps', usage_journey_step_ids)
    request.POST = mutable_post

    return edit_object(request, usage_journey_efootprint_id, model_web)


def add_new_server(request):
    model_web = ModelWeb(request.session)
    server_type = request.POST.get('type_object_available')

    default_ssd = Storage.ssd(f"{request.POST['name']} default ssd")
    add_new_efootprint_object_to_system(request.session, model_web, default_ssd)
    mutable_post = request.POST.copy()
    mutable_post['storage'] = default_ssd.id
    request.POST = mutable_post

    new_efootprint_obj = create_efootprint_obj_from_post_data(request, model_web, server_type)
    added_obj = add_new_efootprint_object_to_system(request.session, model_web, new_efootprint_obj)
    response = render(
        request, "model_builder/object_cards/server_card.html", {"server": added_obj})

    response["HX-Trigger-After-Swap"] = json.dumps({
        "closePanelAfterSwap": True
    })

    return response


def add_new_service(request, server_efootprint_id):
    model_web = ModelWeb(request.session)
    mutable_post = request.POST.copy()
    mutable_post['server'] = server_efootprint_id
    request.POST = mutable_post
    try:
        new_efootprint_obj = create_efootprint_obj_from_post_data(
            request, model_web, request.POST.get('type_object_available'))

        efootprint_server = model_web.get_web_object_from_efootprint_id(server_efootprint_id).modeling_obj
        efootprint_server.compute_calculated_attributes()

        added_obj = add_new_efootprint_object_to_system(request.session, model_web, new_efootprint_obj)

        response = render(request, "model_builder/object_cards/service_card.html",
                          context={"service": added_obj})

        response["HX-Trigger-After-Swap"] = json.dumps({
            "closePanelAfterSwap": True
        })

        return response

    except Exception as e:
        return render_exception_modal(request, e)


def add_new_job(request, usage_journey_step_efootprint_id):
    model_web = ModelWeb(request.session)
    usage_journey_step_to_edit = model_web.get_web_object_from_efootprint_id(usage_journey_step_efootprint_id)

    try:
        new_efootprint_obj = create_efootprint_obj_from_post_data(
            request, model_web, request.POST.get('type_object_available'))
    except Exception as e:
        return render_exception_modal(request, e)

    added_obj = add_new_efootprint_object_to_system(request.session, model_web, new_efootprint_obj)

    mutable_post = request.POST.copy()
    mutable_post['name'] = usage_journey_step_to_edit.name
    mutable_post['user_time_spent'] = usage_journey_step_to_edit.user_time_spent.rounded_magnitude
    job_ids = [job.efootprint_id for job in usage_journey_step_to_edit.jobs]
    job_ids.append(added_obj.efootprint_id)
    mutable_post.setlist('jobs', job_ids)
    request.POST = mutable_post

    return edit_object(request, usage_journey_step_efootprint_id, model_web)


def add_new_usage_pattern(request):
    model_web = ModelWeb(request.session)
    new_efootprint_obj = create_efootprint_obj_from_post_data(request, model_web, 'UsagePattern')
    added_obj = add_new_efootprint_object_to_system(request.session, model_web, new_efootprint_obj)
    request.session["system_data"]["System"]["uuid-system-1"]["usage_patterns"].append(new_efootprint_obj.id)
    request.session.modified = True

    response = render(
        request, "model_builder/object_cards/usage_pattern_card.html", {"usage_pattern": added_obj})

    response["HX-Trigger-After-Swap"] = json.dumps({
        "updateTopParentLines": {"topParentIds": [added_obj.web_id]},
        "setAccordionListeners": {"accordionIds": [added_obj.web_id]},
        "closePanelAfterSwap": True
    })

    return response
