import json
import uuid

import requests
from django.shortcuts import render

from model_builder.model_web import ModelWeb
from model_builder.object_creation_and_edition_utils import create_efootprint_obj_from_post_data, \
    add_new_efootprint_object_to_system, add_new_object_to_system_from_builder
from model_builder.views_edition import edit_object


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
    structure_dict = {
        'str_attributes': ['name'],
        'items': [
            {'category':'server_type_helper','header': 'Server type','class': '','fields': [
                    {'input_type':'select', 'id':'server_type', 'name' : 'Server type', 'required':True, 'options': [
                        {'label':'Autoscaling', 'value':'autoscaling'},
                        {'label':'OnPremise', 'value':'on_premise'},
                        {'label':'Serverless', 'value':'serverless'}
                    ]}]},
            {'category':'autoscaling','header': 'Server creation helper','class': '', 'fields': [
                    {'input_type': 'select', 'id': 'autoscaling_provider', 'name': 'Provider', 'required':True,
                     'options': all_boavizta_cloud_providers},
                    {'input_type': 'datalist', 'id': 'autoscaling_configuration', 'name': 'Server configuration',
                     'required':True, 'options': instance_types_by_provider},
                    {'input_type': 'input', 'id': 'average_carbon_intensity', 'name': 'Average carbon intensity',
                     'required':True, 'unit': 'g/KWh', 'default': '100'}
                ]
            },
            {'category': 'serverless', 'header': 'Server creation helper', 'class': 'd-none', 'fields': [
                {'input_type': 'select', 'id': 'serverless_provider', 'name': 'Provider', 'required': True,
                 'options': all_boavizta_cloud_providers},
                {'input_type': 'datalist', 'id': 'serverless_configuration', 'name': 'Server configuration',
                 'required':
                    True, 'options': instance_types_by_provider},
                {'input_type': 'input', 'id': 'average_carbon_intensity', 'name': 'Average carbon intensity',
                 'required': True, 'unit': 'g/KWh', 'default': '100'}
            ]
             },
            {'category':'on_premise','header': 'Server creation helper','class': 'd-none','fields': [
                    {'input_type':'input', 'id': 'nb_of_cpu_units', 'name': 'Number of CPU units', 'unit': '',
                     'required':True, 'default': '2'},
                    {'input_type':'input', 'id': 'nb_of_cores_per_cpu_unit', 'name': 'Number of CPU Cores',
                     'required':True, 'unit': 'core', 'default': '24'},
                    {'input_type':'input', 'id': 'nb_of_ram_units', 'name': 'RAM unit', 'unit': 'GB',
                     'required':True, 'default': '12'},
                    {'input_type':'input', 'id': 'ram_quantity_per_unit_in_gb', 'name': 'RAM per unit', 'unit': '',
                     'required':True, 'default': '32'},
                    {'input_type': 'input', 'id': 'average_carbon_intensity', 'name': 'Average carbon intensity',
                     'unit': 'g/KWh', 'required':True, 'default': '100'}]}],
        'switch_item': 'server_type',
        'dynamic_lists':[
            {'input':'autoscaling_configuration','filter_by':'autoscaling_provider',
             'list_value': instance_types_by_provider},
            {'input': 'serverless_configuration', 'filter_by': 'serverless_provider',
             'list_value': instance_types_by_provider}
        ]
    }

    http_response = render(request, f"model_builder/side_panels/server_add.html",
                  context={
                      'structure_dict': structure_dict
                  })

    http_response["HX-Trigger-After-Swap"] = "initAddPanel"

    return http_response


def add_new_user_journey(request):
    model_web = ModelWeb(request.session)
    if request.POST.getlist("form_add_uj_steps"):
        new_efootprint_obj = create_efootprint_obj_from_post_data(request, model_web, 'UserJourney')
        added_obj = add_new_efootprint_object_to_system(request, model_web, new_efootprint_obj)
        response = render(
            request, "model_builder/object_cards/user_journey_card.html", {"user_journey": added_obj})
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
            request.session["empty_objects"] = {"UserJourney": {empty_uj_id: added_obj}}
        else:
            if "UserJourney" not in request.session["empty_objects"]:
                request.session["empty_objects"]["UserJourney"] = {empty_uj_id: added_obj}
            else:
                request.session["empty_objects"]["UserJourney"][empty_uj_id] = added_obj
            request.session.modified = True

        response = render(request, "model_builder/object_cards/user_journey_empty.html",
                  context={"user_journey": added_obj})

    return response


def add_new_user_journey_step(request, user_journey_efootprint_id):
    model_web = ModelWeb(request.session)
    new_efootprint_obj = create_efootprint_obj_from_post_data(request, model_web, 'UserJourneyStep')
    added_obj = add_new_efootprint_object_to_system(request, model_web, new_efootprint_obj)
    user_journey_to_edit = model_web.get_web_object_from_efootprint_id(user_journey_efootprint_id)
    mutable_post = request.POST.copy()
    for key in list(mutable_post.keys()):
        if key.startswith('form_add'):
            del mutable_post[key]
    mutable_post['form_edit_name'] = user_journey_to_edit.name
    user_journey_step_ids = []
    for uj_step in user_journey_to_edit.uj_steps:
        user_journey_step_ids.append(uj_step.efootprint_id)
    user_journey_step_ids.append(added_obj.efootprint_id)
    mutable_post.setlist('form_edit_uj_steps', user_journey_step_ids)
    request.POST = mutable_post
    return edit_object(request, user_journey_efootprint_id, model_web)


def add_new_server(request):
    model_web = ModelWeb(request.session)
    server_type = request.POST.get('form_add_server_type')
    server_added = add_new_object_to_system_from_builder(request, model_web, server_type)
    response = render(
        request, "model_builder/object_cards/server_card.html", {"server": server_added})

    return response


def open_create_service_panel(request, server_efootprint_id):
    helper_text = ('The following jobs types are now available to add to your usage journey steps and connect to your '
                   'infrastrusture')
    gen_ai_models = {'open_ai':['gpt3', 'gpt4', 'o1'], 'google':['Gemini', 'Gemini Pro']}
    structure_dict = {
        'str_attributes': ['name'],
        'items': [
            {'category': 'services_available', 'header': 'Services available for this server', 'class': '', 'fields': [
                {'input_type': 'select', 'id': 'type_service_available', 'name': 'Service', 'required': True,
                 'options': [
                    {'label':'Web Application', 'value':'web_app'},
                    {'label':'Gen AI Service', 'value':'gen_ai'},
                    {'label':'Streaming', 'value':'streaming'}
                ]}]},
            {'category': 'web_app', 'header': 'Server creation helper', 'class': '', 'fields': [
                {'input_type': 'input', 'id': 'base_ram_consumption', 'name': 'Base RAM consumption', 'unit': 'GB',
                 'required': True, 'default': '2'},
                {'input_type': 'input', 'id': 'base_cpu_consumption', 'name': 'Base CPU consumption', 'unit': 'cores',
                 'required': True, 'default': '2'},
                {'input_type': 'input', 'id': 'base_storage_consumption', 'name': 'Base Storage consumption',
                 'unit': 'GB',
                 'required': True, 'default': '100'},
                {'input_type': 'select', 'id': 'technology', 'name': 'Technology installed', 'required': True,
                 'options': [
                    {'label':'Python', 'value':'python'},
                    {'label':'Java', 'value':'java'},
                    {'label':'Node.js', 'value':'nodejs'},
                    {'label':'C#', 'value':'csharp'},
                    {'label':'Ruby', 'value':'ruby'},
                    {'label':'PHP', 'value':'php'},
                    {'label':'Go', 'value':'go'},
                    {'label':'Rust', 'value':'rust'},
                    {'label':'Scala', 'value':'scala'},
                    {'label':'Kotlin', 'value':'kotlin'},
                    {'label':'Swift', 'value':'swift'},
                    {'label':'Objective-C', 'value':'objective_c'},
                    {'label':'C++', 'value':'cpp'},
                    {'label':'C', 'value':'c'},
                    {'label':'HTML/CSS/JS', 'value':'html_css_js'},
                    {'label':'Other', 'value':'other'}
                ]},
                {'input_type': 'select', 'id': 'implementation_details', 'name': 'Implementation details',
                 'required':True, 'options': [
                    {'label': 'default', 'value': 'default'},
                    {'label': 'mysql', 'value': 'mysql'},
                    {'label': 'noindex', 'value': 'noindex'},
                    {'label': 'other', 'value': 'other'}
                    ]}
                ]},
            {'category': 'streaming', 'header': 'Server creation helper', 'class': 'd-none', 'fields': [
                {'input_type': 'input', 'id': 'base_ram_consumption', 'name': 'Base RAM consumption', 'unit': 'GB',
                 'required': True, 'default': '2'},
                {'input_type': 'input', 'id': 'base_cpu_consumption', 'name': 'Base CPU consumption', 'unit': 'cores',
                 'required': True, 'default': '2'},
                {'input_type': 'input', 'id': 'base_storage_consumption', 'name': 'Base Storage consumption',
                 'unit': 'GB',
                 'required': True, 'default': '100'},
                {'input_type': 'select', 'id': 'video_resolution', 'name': 'Video resolution', 'required': True,
                 'options': [
                    {'label': '360p', 'value': '360p'},
                    {'label': '480p', 'value': '480p'},
                    {'label': '720p', 'value': '720p'},
                    {'label': '1080p', 'value': '1080p'},
                    {'label': '4K', 'value': '4K'},
                    {'label': '8K', 'value': '8K'}
                 ]}
            ]},
            {'category': 'gen_ai', 'header': 'Server creation helper', 'class': 'd-none', 'fields': [
                {'input_type': 'input', 'id': 'base_ram_consumption', 'name': 'Base RAM consumption', 'unit': 'GB',
                 'required': True, 'default': '2'},
                {'input_type': 'input', 'id': 'base_cpu_consumption', 'name': 'Base CPU consumption', 'unit': 'cores',
                 'required': True, 'default': '2'},
                {'input_type': 'input', 'id': 'base_storage_consumption', 'name': 'Base Storage consumption',
                 'unit': 'GB',
                 'required': True, 'default': '100'},
                {'input_type': 'select', 'id': 'gen_ai_provider', 'name': 'Provider', 'required': True, 'options': [
                     {'label': 'Google', 'value': 'google'},
                     {'label': 'Open AI', 'value': 'open_ai'}
                 ]},
                {'input_type': 'datalist', 'id': 'gen_ai_model', 'name': 'Model', 'required': True, 'options':
                    gen_ai_models}
            ]},
            {'category': 'job_types_associated', 'header': 'Job types associated', 'class': 'd-none',
             'fields': [
                {'input_type' : 'p', 'id': 'job_types_associated_p', 'text': helper_text},
                {'input_type': 'list', 'id': 'job_types_associated_list', 'options': [
                    'Job type 1', 'Job type 2', 'Job type 3']}]}],
        'switch_item': 'type_service_available',
        'dynamic_lists':[
            {'input':'gen_ai_model','filter_by':'gen_ai_provider', 'list_value': gen_ai_models}
        ]
    }
    http_response = render(
        request, "model_builder/side_panels/service_add.html", {
            "server_id": server_efootprint_id,
            "structure_dict": structure_dict
        })

    http_response["HX-Trigger-After-Swap"] = "initAddPanel"

    return http_response


def add_new_service(request, server_efootprint_id):
    model_web = ModelWeb(request.session)
    server = model_web.get_web_object_from_efootprint_id(server_efootprint_id)
    service_id = str(uuid.uuid4())[:6]
    added_obj = {
        "id": service_id,
        "name": request.POST["form_add_name"],
        "server": server,
        "service_type" : request.POST["form_add_server_available"],
        "cpu_required": request.POST["form_add_cpu_required"],
        "ram_required": request.POST["form_add_ram_required"],
        "storage_required": request.POST["form_add_storage_required"]
    }

    if "interface_objects" not in request.session:
        request.session["interface_objects"] = {"Service": {id: added_obj}}
    else:
        if "Service" not in request.session["interface_objects"]:
            request.session["interface_objects"]["Service"] = {service_id: added_obj}
        else:
            request.session["interface_objects"]["Service"][service_id] = added_obj
        request.session.modified = True

    return None
