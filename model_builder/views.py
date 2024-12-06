import logging

from efootprint.api_utils.json_to_system import json_to_system
from efootprint.api_utils.system_to_json import system_to_json
from efootprint.utils.plot_emission_diffs import EmissionPlotter

from model_builder.object_creation_utils import add_new_object_to_system, edit_object_in_system
from model_builder.web_models import ModelWeb
from utils import htmx_render

import json
from django.shortcuts import render
import os
from django.http import HttpResponse
from django.template.loader import render_to_string
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
import io
import base64

matplotlib.use('Agg')
DEFAULT_GRAPH_WIDTH = 700


def model_builder_main(request):
    try:
        jsondata = request.session["system_data"]
    except KeyError:
        with open(os.path.join("model_builder", "default_system_data.json"), "r") as file:
            jsondata = json.load(file)
            request.session["system_data"] = jsondata

    model_web = ModelWeb(jsondata)

    return htmx_render(
        request, "model_builder/model-builder-main.html", context={"model_web": model_web})


def open_create_object_panel(request, object_type):
    model_web = ModelWeb(request.session["system_data"])
    new_object_structure = model_web.get_object_structure(object_type)

    context_data = {
        "form_target_url": "add-new-object",
        "output_button_label": "Save",
        "object_structure": new_object_structure
    }

    return render(request, "model_builder/object-creation-or-edition-form.html", context=context_data)


def open_edit_object_panel(request, object_id):
    model_web = ModelWeb(request.session["system_data"])
    obj_to_edit = model_web.get_object_from_id(object_id)

    context_data = {
        "object_to_edit": obj_to_edit
    }

    return render(request, "model_builder/edit_object_panel.html", context=context_data)


def create_object_addition_or_edition_oob_html_updated(request, objects_to_update):
    #system_footprint_html = system.plot_footprints_by_category_and_object(
    #    height=400, width=DEFAULT_GRAPH_WIDTH, return_only_html=True)

    #graph_container_html = render_to_string(
    #    "model_builder/graph-container.html",
    #    context={"systemFootprint": system_footprint_html, "hx_swap_oob": True})

    #model_comparison_buttons_html = render_to_string(
    #    "model_builder/model-comparison-buttons.html",
    #    {"is_different_from_ref_model": request.session["system_data"] != request.session["reference_system_data"],
    #    "hx_swap_oob": True})

    #return_html = graph_container_html + model_comparison_buttons_html

    return_html = ""

    template_dict = {
        'UsagePattern': 'usage_pattern.html',
        'UserJourney': 'user_journey_card.html',
        'UserJourneyStep': 'user_journey_step_card.html',
        'Job': 'job_card.html',
        'Autoscaling': 'infrastructure_card.html',
        'OnPremise': 'infrastructure_card.html',
        'Serverless': 'infrastructure_card.html'
    }

    key_obj_dict = {
        'UsagePattern': 'usage_pattern',
        'UserJourney': 'user_journey',
        'UserJourneyStep': 'user_journey_step',
        'Job': 'job',
        'Autoscaling': 'server',
        'OnPremise': 'server',
        'Serverless': 'server'
    }

    for obj in objects_to_update:
        template_name= template_dict[obj.class_as_simple_str]
        key_obj= key_obj_dict[obj.class_as_simple_str]
        return_html += render_to_string(
            f"model_builder/model_part/card/{template_name}",
            {key_obj: obj,
             "hx_swap_oob": True}
        )

    #for obj in objects_to_update:
    #    return_html += render_to_string(
    #        "model_builder/object-card.html",
    #       {"object": obj, "hx_swap_oob": True})

    request.session["img_base64"] = None

    return return_html


def add_new_object(request):
    model_web = ModelWeb(request.session["system_data"])
    added_obj, objects_to_update = add_new_object_to_system(request, model_web)
    oob_html = create_object_addition_or_edition_oob_html_updated(request, model_web.system, objects_to_update)

    http_response = HttpResponse(oob_html)

    return http_response


def edit_object(request, object_id):
    model_web = ModelWeb(request.session["system_data"])
    obj_to_edit = model_web.get_object_from_id(object_id)
    (edited_obj, objects_to_update) = edit_object_in_system(request, obj_to_edit)
    #(edited_obj, objects_to_update, obj_ids_of_connections_to_add,
    # obj_ids_of_connections_to_remove) = edit_object_in_system(request, obj_to_edit)
    oob_html = create_object_addition_or_edition_oob_html_updated(request, objects_to_update)

    http_response = HttpResponse(oob_html)
    # TODO: update below logic to handle link updates
    #http_response["HX-Trigger-After-Swap"] = json.dumps(
    #    {"editConnections": {"editedNode": edited_obj.id,
    #                         "connectionsToAdd": obj_ids_of_connections_to_add,
    #                         "connectionsToRemove": obj_ids_of_connections_to_remove}})

    return http_response


def delete_object(request):
    model_web = ModelWeb(request.session["system_data"])

    obj_id = request.POST["object-id"]
    obj_type = request.POST["object-type"]

    system = model_web.system
    if obj_type == "UsagePattern":
        system.usage_patterns = [up for up in system.usage_patterns if up.id != obj_id]

    model_web.flat_obj_dict[obj_id].self_delete()
    model_web.response_objs[obj_type].pop(obj_id, None)
    model_web.flat_obj_dict.pop(obj_id, None)

    request.session["system_data"] = system_to_json(system, save_calculated_attributes=False)

    if obj_type != "UsagePattern":
        http_response = HttpResponse(status=204)
    else:
        system_footprint_html = system.plot_footprints_by_category_and_object(
            height=400, width=DEFAULT_GRAPH_WIDTH, return_only_html=True)

        graph_container_html = render_to_string(
            "model_builder/graph-container.html",
            context={"systemFootprint": system_footprint_html, "hx_swap_oob": True})

        model_comparison_buttons_html = render_to_string(
            "model_builder/model-comparison-buttons.html",
            {"is_different_from_ref_model": request.session["system_data"] != request.session["reference_system_data"],
             "hx_swap_oob": True})

        return_html = graph_container_html + model_comparison_buttons_html
        request.session["img_base64"] = None

        for up in system.usage_patterns:
            return_html += render_to_string(
                "model_builder/object-card.html",
                {"object": up, "hx_swap_oob": True})

        http_response = HttpResponse(return_html)

    # TODO: Update below logic
    http_response["HX-Trigger"] = json.dumps({"deleteObject": {"ObjectId": obj_id}})

    return http_response


def download_json(request):
    data = request.session.get('system_data', {})
    json_data = json.dumps(data, indent=4)
    response = HttpResponse(json_data, content_type='application/json')
    response['Content-Disposition'] = f'attachment; filename="efootprint-model-system-data.json"'

    return response


def set_as_reference_model(request):
    request.session["reference_system_data"] = request.session["system_data"]

    return render(request, "model_builder/model-comparison-buttons.html", {"is_different_from_ref_model": False})


def reset_model_reference(request):
    request.session["system_data"] = request.session["reference_system_data"]
    request.session["img_base64"] = None

    return model_builder_main(request)


def compare_with_reference(request):
    ref_response_objs, ref_flat_obj_dict = json_to_system(request.session["reference_system_data"])
    response_objs, flat_obj_dict = json_to_system(request.session["system_data"])

    ref_system = list(ref_response_objs["System"].values())[0]
    system = list(response_objs["System"].values())[0]

    emissions_dict__old = [ref_system.initial_total_energy_footprints_sum_over_period,
                           ref_system.initial_total_fabrication_footprints_sum_over_period]
    emissions_dict__new = [system.total_energy_footprint_sum_over_period,
                           system.total_fabrication_footprint_sum_over_period]

    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(9, 6))
    EmissionPlotter(
        ax, emissions_dict__old, emissions_dict__new, rounding_value=1).plot_emission_diffs()

    # Convert plot to binary buffer
    buf = io.BytesIO()
    canvas = FigureCanvasAgg(fig)
    canvas.print_png(buf)

    # Encode binary buffer as base64
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode()

    # Close plot to free memory
    plt.close(fig)

    request.session['img_base64'] = img_base64

    return render(request, "model_builder/compare-container.html", {"img_base64": img_base64})
