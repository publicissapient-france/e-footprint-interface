from django.db.models.fields import return_None

from model_builder.model_web import ModelWeb
from utils import htmx_render

import json
import os
from django.http import HttpResponse, JsonResponse
import matplotlib

matplotlib.use('Agg')
DEFAULT_GRAPH_WIDTH = 700


def model_builder_main(request):
    if "system_data" not in request.session.keys():
        with open(os.path.join("model_builder", "default_system_data.json"), "r") as file:
            system_data = json.load(file)
            request.session["system_data"] = system_data

    model_web = ModelWeb(request.session)
    context = {"model_web": model_web}

    if request.session.get('interface_objects'):
        context['interface_objects'] = request.session['interface_objects']

    http_response = htmx_render(
        request, "model_builder/model-builder-main.html", context=context)

    if request.headers.get("HX-Request") == "true":
        http_response["HX-Trigger-After-Swap"] = "initLeaderLines"

    return http_response


def download_json(request):
    data = request.session.get('system_data', {})
    json_data = json.dumps(data, indent=4)
    response = HttpResponse(json_data, content_type='application/json')
    response['Content-Disposition'] = f'attachment; filename="efootprint-model-system-data.json"'

    return response


def get_jobs_type_link_to_service_type(request, service_id):
    job_types_data={
        'web_app': [
            {
                'label': 'Upload',
                'value': 'upload',
                'data_upload': '800',
                'data_download': '0.01',
                'data_stored': '100',
                'request_duration': '5',
                'ram_needed': '100',
                'cpu_needed': '1'
            },
            {
                'label': 'Download',
                'value': 'download',
                'data_upload': '5',
                'data_download': '1',
                'data_stored': '1',
                'request_duration': '10',
                'ram_needed': '200',
                'cpu_needed': '2'},
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

    installed_services = request.session['interface_objects']['installed_services']
    for server in installed_services:
        for service in server['services']:
            if service['id'] == service_id:
                service_type =  service['service_type']

    return JsonResponse(job_types_data.get(service_type, []), safe=False)
