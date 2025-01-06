import uuid
from copy import copy

from efootprint.api_utils.json_to_system import json_to_system
from efootprint.api_utils.system_to_json import system_to_json
from efootprint.utils.plot_emission_diffs import EmissionPlotter

from model_builder.object_creation_utils import add_new_object_to_system, edit_object_in_system
from model_builder.model_web import ModelWeb
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
    if "system_data" not in request.session.keys():
        with open(os.path.join("model_builder", "default_system_data.json"), "r") as file:
            system_data = json.load(file)
            request.session["system_data"] = system_data

    model_web = ModelWeb(request.session)

    http_response = htmx_render(
        request, "model_builder/model-builder-main.html", context={"model_web": model_web})

    if request.headers.get("HX-Request") == "true":
        http_response["HX-Trigger-After-Swap"] = "initLeaderLines"

    return http_response


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

    return render(request, f"model_builder/model_part/add/{template_name}", context=context_data)


def open_edit_object_panel(request, object_id):
    model_web = ModelWeb(request.session)
    obj_to_edit = model_web.get_web_object_from_efootprint_id(object_id)

    return render(request, "model_builder/edit_object_panel.html", context={"object_to_edit": obj_to_edit})


def create_object_addition_or_edition_oob_html_updated(request, objects_to_update):
    return_html = ""
    for obj in objects_to_update:
        if obj.class_as_simple_str not in ['Country', 'Network', 'Hardware', 'Storage']:
            template_name= f'{obj.template_name}_card.html'
            key_obj= obj.template_name
            return_html += render_to_string(
                f"model_builder/model_part/card/{template_name}",
                {key_obj: obj,
                 "hx_swap_oob": True}
            )

    return return_html


def add_new_object(request):
    return None


def add_new_user_journey(request):
    model_web = ModelWeb(request.session)
    if request.POST.getlist("form_add_uj_steps"):
        added_obj = add_new_object_to_system(request, model_web, 'UserJourney')
        response = render(
            request, "model_builder/model_part/card/user_journey_card.html", {"user_journey": added_obj})
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

        response = render(request, "model_builder/model_part/card/user_journey_empty.html",
                  context={"user_journey": added_obj})

    return response

def add_new_user_journey_step(request, user_journey_efootprint_id):
    model_web = ModelWeb(request.session)
    added_obj = add_new_object_to_system(request, model_web, 'UserJourneyStep')
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


def edit_object(request, object_id, model_web=None):
    if model_web is None:
        model_web = ModelWeb(request.session)
    data_attribute_updates = []
    ids_of_web_elements_with_lines_to_remove = []
    obj_to_edit = model_web.get_web_object_from_efootprint_id(object_id)
    accordion_children_before_edit = {}
    for duplicated_card in obj_to_edit.duplicated_cards:
        accordion_children_before_edit[duplicated_card] = copy(duplicated_card.accordion_children)

    edited_obj = edit_object_in_system(request, obj_to_edit)
    accordion_children_after_edit = {}
    for duplicated_card in edited_obj.duplicated_cards:
        accordion_children_after_edit[duplicated_card] = copy(duplicated_card.accordion_children)

    assert accordion_children_before_edit.keys() == accordion_children_after_edit.keys()

    response_html = ""
    for duplicated_card in accordion_children_before_edit.keys():
        response_html += f"<p hx-swap-oob='innerHTML:#button-{duplicated_card.web_id}'>{duplicated_card.name}</p>"
        added_accordion_children = [acc_child for acc_child in accordion_children_after_edit[duplicated_card]
                                    if acc_child not in accordion_children_before_edit[duplicated_card]]

        removed_accordion_children = [acc_child for acc_child in accordion_children_before_edit[duplicated_card]
                                      if acc_child not in accordion_children_after_edit[duplicated_card]]

        for removed_accordion_child in removed_accordion_children:
            response_html += f"<div hx-swap-oob='delete:#{removed_accordion_child.web_id}'></div>"
            ids_of_web_elements_with_lines_to_remove.append(removed_accordion_child.web_id)
            index_removed_accordion_child = accordion_children_before_edit[duplicated_card].index(
                removed_accordion_child)
            if index_removed_accordion_child >= 1:
                previous_accordion = accordion_children_before_edit[duplicated_card][index_removed_accordion_child-1]
                if previous_accordion not in removed_accordion_children:
                    data_attribute_updates += previous_accordion.data_attributes_as_list_of_dict

        unchanged_children = [acc_child for acc_child in accordion_children_after_edit[duplicated_card]
                              if acc_child not in added_accordion_children]

        added_children_html = ""
        for added_accordion_child in added_accordion_children:
            added_children_html += render_to_string(
                f"model_builder/model_part/card/{added_accordion_child.template_name}_card.html",
                {added_accordion_child.template_name: added_accordion_child})

        if unchanged_children and added_accordion_children:
            last_unchanged_child = unchanged_children[-1]
            data_attribute_updates += last_unchanged_child.data_attributes_as_list_of_dict
            response_html += (f"<div hx-swap-oob='afterend:#{last_unchanged_child.web_id}'>"
                                  f"{added_children_html}</div>")

        elif added_accordion_children and not unchanged_children:
            response_html += (f"<div hx-swap-oob='beforeend:#flush-{duplicated_card.web_id} "
                              f".accordion-body'>{added_children_html}</div>")

    http_response = HttpResponse(response_html)

    for duplicated_card in edited_obj.duplicated_cards:
        data_attribute_updates += duplicated_card.data_attributes_as_list_of_dict
        for parent in duplicated_card.all_accordion_parents:
            data_attribute_updates += parent.data_attributes_as_list_of_dict

    top_parent_ids = list(set([duplicated_card.top_parent.web_id for duplicated_card in
                                   edited_obj.duplicated_cards]))

    http_response["HX-Trigger"] = json.dumps({
        "removeLinesAndUpdateDataAttributes": {
            "elementIdsOfLinesToRemove": ids_of_web_elements_with_lines_to_remove,
            "dataAttributeUpdates": data_attribute_updates
        }
    })

    http_response["HX-Trigger-After-Swap"] = json.dumps({
        "updateTopParentLines": {
            "topParentIds": top_parent_ids
        }
    })

    return http_response

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
    ref_response_objs, ref_flat_efootprint_objs_dict = json_to_system(request.session["reference_system_data"])
    response_objs, flat_efootprint_objs_dict = json_to_system(request.session["system_data"])

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


