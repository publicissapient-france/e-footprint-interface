from django.db.models.fields import return_None

from model_builder.model_web import ModelWeb
from utils import htmx_render

import json
import os
from django.http import HttpResponse, JsonResponse
import matplotlib

matplotlib.use('Agg')
DEFAULT_GRAPH_WIDTH = 700


def model_builder_main(request, reboot=False):
    if "system_data" not in request.session.keys() or reboot=="reboot":
        if "empty_objects" in request.session.keys():
            del request.session["empty_objects"]
        with open(os.path.join("model_builder", "default_system_data.json"), "r") as file:
            system_data = json.load(file)
            request.session["system_data"] = system_data

    model_web = ModelWeb(request.session)
    http_response = htmx_render(
        request, "model_builder/model-builder-main.html", context={"model_web": model_web})

    if request.headers.get("HX-Request") == "true":
        http_response["HX-Trigger-After-Swap"] = "initLeaderLines"

    return http_response


def download_json(request):
    data = request.session.get('system_data', {})
    json_data = json.dumps(data, indent=4)
    response = HttpResponse(json_data, content_type='application/json')
    response['Content-Disposition'] = f'attachment; filename="efootprint-model-system-data.json"'

    return response
