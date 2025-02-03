from django.shortcuts import redirect

from model_builder.model_web import ModelWeb
from utils import htmx_render

import json
import os
from django.http import HttpResponse
import matplotlib

matplotlib.use('Agg')
DEFAULT_GRAPH_WIDTH = 700


def model_builder_main(request, reboot=False):
    if reboot and reboot != "reboot":
        raise ValueError("reboot must be False or 'reboot'")
    if reboot == "reboot":
        if "empty_objects" in request.session.keys():
            del request.session["empty_objects"]
        with open(os.path.join("model_builder", "default_system_data.json"), "r") as file:
            system_data = json.load(file)
            request.session["system_data"] = system_data
        return redirect("model-builder")
    if "system_data" not in request.session.keys():
        return redirect("model-builder", reboot="reboot")

    model_web = ModelWeb(request.session, launch_system_computations=False)

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


def result_chart(request):
    model_web = ModelWeb(request.session, launch_system_computations=True)

    http_response = htmx_render(
        request, "model_builder/resultPanel.html", context={'model_web': model_web})

    http_response["HX-Trigger-After-Swap"] = "computeResultChart"

    return http_response
