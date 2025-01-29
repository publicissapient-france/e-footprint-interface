import json
import os
import uuid

import requests
from efootprint.core.all_classes_in_order import SERVER_CLASSES

from e_footprint_interface import settings
from django.shortcuts import render

from model_builder.class_structure import efootprint_class_structure
from model_builder.model_web import ModelWeb
from model_builder.object_creation_and_edition_utils import create_efootprint_obj_from_post_data, \
    add_new_efootprint_object_to_system, create_new_usage_pattern_from_post_data
from model_builder.views_edition import edit_object

def get_form_structure(form_type):
    with open(os.path.join(settings.BASE_DIR, 'theme', 'static', 'form_inputs.json'), "r") as form_inputs_file:
        form_inputs = json.load(form_inputs_file)
    return form_inputs[form_type]

def open_create_object_panel(request, object_type):
    model_web = ModelWeb(request.session)
    new_object_structure = model_web.get_object_structure(object_type)
    template_name = f'{new_object_structure.template_name}_add.html'
    context_data = {"object_structure": new_object_structure,
                    "header_name": "Create " +  new_object_structure.template_name.replace("_", " "),
                    "new_object_name": "New " + new_object_structure.template_name.replace("_", " ")}
    if request.GET.get('efootprint_id_of_parent_to_link_to'):
        context_data['efootprint_id_of_parent_to_link_to'] = request.GET['efootprint_id_of_parent_to_link_to']
    if request.GET.get("name"):
        context_data["new_object_name"] = request.GET["name"]
    if request.GET.get("efootprint_id_of_empty_object_origin"):
        context_data["efootprint_id_of_empty_object_origin"] = request.GET["efootprint_id_of_empty_object_origin"]

    return render(request, f"model_builder/side_panels/{template_name}", context=context_data)


def open_create_server_panel(request):
    boavizta_cloud_providers_request_result = json.loads(
        requests.get(
            "https://api.boavizta.org/v1/cloud/instance/all_providers", headers={'accept': 'application/json'}
        ).content.decode('utf-8')
    )
    all_boavizta_cloud_providers = []
    for provider in boavizta_cloud_providers_request_result:
        all_boavizta_cloud_providers.append({'label': provider, 'value': provider})
    instance_types_by_provider = {}
    for cloud_provider in boavizta_cloud_providers_request_result:
        instance_types_by_provider[cloud_provider] = json.loads(
            requests.get(
                f"https://api.boavizta.org/v1/cloud/instance/all_instances",
                headers={'accept': 'application/json'}, params = {"provider": cloud_provider}
            ).content.decode('utf-8')
        )

    structure_dict = get_form_structure('Server')
    for item in structure_dict['items']:
        for field in item['fields']:
            if field['id'].endswith('_provider'):
                field['options'] = all_boavizta_cloud_providers
            if field['id'].endswith('_configuration'):
                field['options'] = all_boavizta_cloud_providers
    for item in structure_dict['dynamic_lists']:
        if item['filter_by'].endswith('_provider'):
            item['list_value'] = instance_types_by_provider

    http_response = render(request, f"model_builder/side_panels/server_add.html",
                  context={
                      'structure_dict': structure_dict
                  })

    http_response["HX-Trigger-After-Swap"] = "initAddPanel"

    return http_response

def generate_object_creation_structure(available_efootprint_classes: list, header: str):
    efootprint_classes_dict = {"str_attributes": ["name"], "switch_item": "type_service_available"}
    type_efootprint_classes_available = {
        "category": "efootprint_classes_available",
        "header": header,
        "class": "",
        "fields": [{
            "input_type": "select",
            "id": "type_service_available",
            "name": "Service",
            "required": True,
            "options": [{"label": service.__name__, "value": service.__name__}
                        for service in available_efootprint_classes]
        }
        ]
    }

    efootprint_classes_dict["items"] = [type_efootprint_classes_available]
    efootprint_classes_dict["dynamic_lists"] = []

    for index, efootprint_class in enumerate(available_efootprint_classes):
        class_fields = []
        class_structure = efootprint_class_structure(efootprint_class.__name__)
        for str_attribute, str_attribute_values in class_structure["str_attributes"].items():
            class_fields.append({
                "input_type": "select",
                "id": str_attribute,
                "name": str_attribute,
                "required": True,
                "options": [{"label": attr_value, "value": attr_value} for attr_value in str_attribute_values]
            })
        for numerical_attribute in class_structure["numerical_attributes"]:
            class_fields.append({
                "input_type": "input",
                "id": numerical_attribute["attr_name"],
                "name": numerical_attribute["attr_name"],
                "unit": numerical_attribute["unit"],
                "required": True,
                "default": numerical_attribute["default_value"]
            })
        for conditional_str_attribute, conditional_str_attribute_value \
            in class_structure["conditional_str_attributes"].items():
            class_fields.append({
                "input_type": "datalist",
                "id": conditional_str_attribute,
                "name": conditional_str_attribute,
                "options": None
            })
            efootprint_classes_dict["dynamic_lists"].append(
                {
                    "input": conditional_str_attribute,
                    "filter_by": conditional_str_attribute_value["depends_on"],
                    "list_value": conditional_str_attribute_value["conditional_list_values"]
                })
        service_class = "d-none"
        if index == 0:
            service_class = ""
        efootprint_classes_dict["items"].append({
            "category": efootprint_class.__name__,
            "header": f"{efootprint_class.__name__} creation",
            "class": service_class,
            "fields": class_fields})

    return efootprint_classes_dict


def open_create_service_panel(request, server_efootprint_id):
    server_class = None
    for efootprint_server_class in SERVER_CLASSES:
        if server_efootprint_id in request.session["system_data"][efootprint_server_class.__name__].keys():
            server_class = efootprint_server_class
            break

    assert server_class is not None, f"Server with efootprint_id {server_efootprint_id} not found in system data"

    installable_services = server_class.installable_services()
    services_dict = generate_object_creation_structure(installable_services, "Services available for this server")

    http_response = render(
        request, "model_builder/side_panels/service_add.html", {
            "server_id": server_efootprint_id,
            "structure_dict": services_dict
        })

    http_response["HX-Trigger-After-Swap"] = "initAddPanel"

    return http_response

def open_create_job_panel(request):
    structure_dict = get_form_structure('Job')
    model_web = ModelWeb(request.session)

    if request.GET.get('efootprint_id_of_parent_to_link_to'):
        efootprint_id_of_parent_to_link_to= request.GET['efootprint_id_of_parent_to_link_to']
    job_types_data = {
        'web_app': [
            {
                'label': 'Upload',
                'value': 'upload',
                'predefined_value': [
                    {'name': 'data_upload', 'value': '800'},
                    {'name': 'data_download', 'value': '0.01'},
                    {'name': 'data_stored', 'value': '100'},
                    {'name': 'request_duration', 'value': '5'},
                    {'name': 'ram_needed', 'value': '100'},
                    {'name': 'cpu_needed', 'value': '1'}
                ]
            },
            {
                'label': 'Download',
                'value': 'download',
                'predefined_value': [
                    {'name': 'data_upload', 'value': '5'},
                    {'name': 'data_download', 'value': '1'},
                    {'name': 'data_stored', 'value': '1'},
                    {'name': 'request_duration', 'value': '10'},
                    {'name': 'ram_needed', 'value': '200'},
                    {'name': 'cpu_needed', 'value': '2'}

                ]
            },
            {'label': 'Login', 'value': 'login'}
        ],
        'gen_ai': [
            {'label': 'Chat', 'value': 'chat'},
            {'label': 'Image generation', 'value': 'image_generation'}
        ],
        'streaming': [
            {'label': 'Video', 'value': 'video'},
            {'label': 'Audio', 'value': 'audio'}
        ]
    }

    servers = model_web.get_web_objects_from_efootprint_type("Autoscaling") + \
              model_web.get_web_objects_from_efootprint_type("Serverless") + \
              model_web.get_web_objects_from_efootprint_type("OnPremise")
    server_options = [{'label': server.name, 'value': server.efootprint_id} for server in servers]
    structure_dict['items'][0]['fields'][0]['options'] = server_options

    installed_services = request.session.get("interface_objects", {}).get("installed_services", [])
    services_options = []
    list_services = {}
    for server in installed_services:
        server_services = []
        for service in server["services"]:
            server_services.append({'label': service["name"], 'value': service["id"]})
            services_options.append({'label': service["name"], 'value': service["id"]})
        list_services[server["server_id"]] = server_services
    structure_dict['items'][0]['fields'][1]['options'] = services_options
    structure_dict['dynamic_lists'][0]['list_value'] = list_services

    init_service_type = installed_services[0]["services"][0]["service_type"]

    structure_dict['items'][0]['fields'][2]['options'] = job_types_data[init_service_type]

    http_response = render(
        request, "model_builder/side_panels/job_add.html", {
            "structure_dict": structure_dict,
            "efootprint_id_of_parent_to_link_to": efootprint_id_of_parent_to_link_to
        })
    http_response["HX-Trigger-After-Swap"] = "initAddPanel"

    return http_response

def open_create_usage_pattern_panel(request):
    model_web = ModelWeb(request.session)
    usage_journeys = model_web.get_efootprint_objects_from_efootprint_type("UserJourney")
    networks = model_web.get_web_objects_from_efootprint_type("Network")
    countries = model_web.get_web_objects_from_efootprint_type("Country")
    devices = model_web.get_web_objects_from_efootprint_type("Hardware")
    http_response = render(
        request, "model_builder/side_panels/usage_pattern_add.html", {
            "usageJourneys": usage_journeys,
            "networks": networks,
            "countries": countries,
            "devices": devices
        })
    return http_response


def add_new_usage_journey(request):
    model_web = ModelWeb(request.session)
    if request.POST.getlist("form_add_uj_steps"):
        new_efootprint_obj = create_efootprint_obj_from_post_data(request, model_web, 'UsageJourney')
        added_obj = add_new_efootprint_object_to_system(request, model_web, new_efootprint_obj)
        response = render(
            request, "model_builder/object_cards/usage_journey_card.html", {"usage_journey": added_obj})
        response["HX-Trigger-After-Swap"] = json.dumps({
            "updateTopParentLines": {"topParentIds": [added_obj.web_id]},
            "setAccordionListeners": {"accordionIds": [added_obj.web_id]}})
    else:
        if not request.POST.get("efootprint_id_of_empty_object_origin"):
            empty_uj_id = f"new-uj-{str(uuid.uuid4())[:6]}"
        else:
            empty_uj_id = request.POST["efootprint_id_of_empty_object_origin"]
        added_obj = {
            "name": request.POST["form_add_name"],
            "web_id": empty_uj_id,
            "efootprint_id": empty_uj_id,
            "links_to": "",
            "data_line_opt": "",
            "uj_steps": [],
            "list_attributes": [{"attr_name": "uj_steps", "existing_objects": []}]
        }

        if "empty_objects" not in request.session:
            request.session["empty_objects"] = {"UsageJourney": {empty_uj_id: added_obj}}
        else:
            if "UsageJourney" not in request.session["empty_objects"]:
                request.session["empty_objects"]["UsageJourney"] = {empty_uj_id: added_obj}
            else:
                request.session["empty_objects"]["UsageJourney"][empty_uj_id] = added_obj
            request.session.modified = True

        response = render(request, "model_builder/object_cards/usage_journey_empty.html",
                  context={"usage_journey": added_obj})

    return response


def add_new_usage_journey_step(request, usage_journey_efootprint_id):
    model_web = ModelWeb(request.session)
    new_efootprint_obj = create_efootprint_obj_from_post_data(request, model_web, 'UsageJourneyStep')
    added_obj = add_new_efootprint_object_to_system(request, model_web, new_efootprint_obj)
    usage_journey_to_edit = model_web.get_web_object_from_efootprint_id(usage_journey_efootprint_id)
    mutable_post = request.POST.copy()
    for key in list(mutable_post.keys()):
        if key.startswith('form_add'):
            del mutable_post[key]
    mutable_post['form_edit_name'] = usage_journey_to_edit.name
    usage_journey_step_ids = []
    for uj_step in usage_journey_to_edit.uj_steps:
        usage_journey_step_ids.append(uj_step.efootprint_id)
    usage_journey_step_ids.append(added_obj.efootprint_id)
    mutable_post.setlist('form_edit_uj_steps', usage_journey_step_ids)
    request.POST = mutable_post
    return edit_object(request, usage_journey_efootprint_id, model_web)


def add_new_server(request):
    model_web = ModelWeb(request.session)
    server_type = request.POST.get('form_add_server_type')
    server_added = add_new_efootprint_object_to_system(request, model_web, server_type)
    response = render(
        request, "model_builder/object_cards/server_card.html", {"server": server_added})

    return response


def add_new_service(request, server_efootprint_id):
    model_web = ModelWeb(request.session)
    server = model_web.get_web_object_from_efootprint_id(server_efootprint_id)
    service_id = str(uuid.uuid4())[:6]
    added_obj = {
        "id": service_id,
        "name": request.POST["form_add_name"],
        "server": server.efootprint_id,
        "service_type" : request.POST["form_add_type_service_available"],
        "cpu_required": request.POST["form_add_base_cpu_consumption"],
        "ram_required": request.POST["form_add_base_ram_consumption"],
        "storage_required": request.POST["form_add_base_cpu_consumption"]
    }
    if request.POST.get("form_add_type_service_available") == 'gen_ai':
        added_obj['gen_ai_provider'] = request.POST["form_add_gen_ai_provider"]
        added_obj['gen_ai_model'] = request.POST["form_add_gen_ai_model"]
    elif request.POST.get("form_add_type_service_available") == 'web_app':
        added_obj['technology'] = request.POST["form_add_technology"]
        added_obj['implementation_details'] = request.POST["form_add_implementation_details"]
    elif request.POST.get("form_add_type_service_available") == 'streaming':
        added_obj['video_resolution'] = request.POST["form_add_video_resolution"]
    else:
        raise ValueError("Service type not recognized")

    if "interface_objects" not in request.session or "installed_services" not in request.session["interface_objects"]:
        request.session["interface_objects"] = {
            "installed_services": [{"server_id": server_efootprint_id,"services": [added_obj]}]}
    else:
        services_list = request.session["interface_objects"]["installed_services"]
        for server_services in services_list:
            if server_services["server_id"] == server_efootprint_id:
                server_services["services"].append(added_obj)
                break
        else:
            services_list.append({"server_id": server_efootprint_id,"services": [added_obj]})

    request.session.modified = True

    response = render(request, "model_builder/object_cards/service_card.html",
                      context={"server": server, 'interface_objects': request.session["interface_objects"]})

    return response

def add_new_job(request, usage_journey_step_efootprint_id):
    model_web = ModelWeb(request.session)
    usage_journey_step_to_edit = model_web.get_web_object_from_efootprint_id(usage_journey_step_efootprint_id)
    job_types_data = {
        'web_app': [
            {
                'label': 'Upload',
                'value': 'upload',
                'predefined_value': [
                    {'name':'data_upload', 'value': '800'},
                    {'name':'data_download', 'value': '0.01'},
                    {'name':'data_stored', 'value': '100'},
                    {'name':'request_duration', 'value': '5'},
                    {'name':'ram_needed', 'value': '100'},
                    {'name':'cpu_needed', 'value':'1'}
                ]
            },
            {
                'label': 'Download',
                'value': 'download',
                'predefined_value': [
                    {'name':'data_upload', 'value': '5'},
                    {'name':'data_download', 'value': '1'},
                    {'name':'data_stored', 'value': '1'},
                    {'name':'request_duration', 'value': '10'},
                    {'name':'ram_needed', 'value': '200'},
                    {'name':'cpu_needed', 'value': '2'}

                ]
            },
            {'label': 'Login', 'value': 'login'}
        ],
        'gen_ai': [
            {'label': 'Chat', 'value': 'chat'},
            {'label': 'Image generation', 'value': 'image_generation'}
        ],
        'streaming': [
            {'label': 'Video', 'value': 'video'},
            {'label': 'Audio', 'value': 'audio'}
        ]
    }
    job_type = request.POST.get('form_add_job_type')

    installed_services = request.session['interface_objects']['installed_services']
    for server in installed_services:
        for service in server['services']:
            if service['id'] == request.POST.get('form_add_service'):
                service_type = service['service_type']

    for job_type_item in job_types_data[service_type]:
        if job_type_item['value'] == job_type:
            new_job = job_type_item
            break

    mutable_post = request.POST.copy()
    for field in new_job['predefined_value']:
        mutable_post[f'form_add_{field["name"]}'] = field['value']
    request.POST = mutable_post
    new_efootprint_obj = create_efootprint_obj_from_post_data(request, model_web, 'Job')
    added_obj = add_new_efootprint_object_to_system(request, model_web, new_efootprint_obj)

    for key in list(mutable_post.keys()):
        if key.startswith('form_add'):
            del mutable_post[key]
    mutable_post['form_edit_name'] = usage_journey_step_to_edit.name
    mutable_post['form_edit_user_time_spent'] = usage_journey_step_to_edit.user_time_spent.rounded_magnitude
    job_ids = []
    for job in usage_journey_step_to_edit.jobs:
        job_ids.append(job.efootprint_id)
    job_ids.append(added_obj.efootprint_id)
    mutable_post.setlist('form_edit_jobs', job_ids)
    request.POST = mutable_post
    return edit_object(request, usage_journey_step_efootprint_id, model_web)



def add_new_usage_pattern(request):
    model_web = ModelWeb(request.session)
    new_efootprint_obj = create_new_usage_pattern_from_post_data(request, model_web)
    added_obj = add_new_efootprint_object_to_system(request, model_web, new_efootprint_obj)
    response = render(
        request, "model_builder/object_cards/usage_pattern_card.html", {"usage_pattern": added_obj})
    response["HX-Trigger-After-Swap"] = json.dumps({
        "updateTopParentLines": {"topParentIds": [added_obj.web_id]},
        "setAccordionListeners": {"accordionIds": [added_obj.web_id]}})
    return response
