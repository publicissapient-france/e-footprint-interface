import json

from django.http import HttpResponse
from django.template.loader import render_to_string
from efootprint.api_utils.system_to_json import system_to_json

from model_builder.model_web import ModelWeb
from model_builder.views import DEFAULT_GRAPH_WIDTH


def delete_object(request):
    model_web = ModelWeb(request.session)

    obj_id = request.POST["object-id"]
    obj_type = request.POST["object-type"]

    system = model_web.system
    if obj_type == "UsagePattern":
        system.usage_patterns = [up for up in system.usage_patterns if up.id != obj_id]

    model_web.flat_efootprint_objs_dict[obj_id].self_delete()
    model_web.response_objs[obj_type].pop(obj_id, None)
    model_web.flat_efootprint_objs_dict.pop(obj_id, None)

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
