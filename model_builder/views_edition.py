import json
from copy import copy

from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from efootprint.core.all_classes_in_order import SERVICE_CLASSES

from model_builder.class_structure import generate_object_edition_structure
from model_builder.model_web import ModelWeb, ATTRIBUTES_TO_SKIP_IN_FORMS
from model_builder.modeling_objects_web import ServerWeb
from model_builder.object_creation_and_edition_utils import edit_object_in_system, render_exception_modal


def open_edit_object_panel(request, object_id):
    model_web = ModelWeb(request.session)
    obj_to_edit = model_web.get_web_object_from_efootprint_id(object_id)
    structure_dict, dynamic_form_data = generate_object_edition_structure(
        obj_to_edit, attributes_to_skip=ATTRIBUTES_TO_SKIP_IN_FORMS)
    if isinstance(obj_to_edit, ServerWeb):
        # TODO: remove when developing the storage edition feature
        structure_dict["modeling_obj_attributes"] = []
    if obj_to_edit.class_as_simple_str in [service_class.__name__ for service_class in SERVICE_CLASSES]:
        structure_dict["modeling_obj_attributes"] = []

    http_response = render(
        request, "model_builder/side_panels/edit_object_panel.html",
        context={"object_to_edit": obj_to_edit, "structure_dict": structure_dict,
                 "dynamic_form_data": dynamic_form_data})

    http_response["HX-Trigger-After-Swap"] = "initAddPanel"

    return http_response


def compute_edit_object_html_and_event_response(request, object_id, model_web=None):
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
            if len(removed_accordion_child.modeling_obj_containers) == 0:
                removed_accordion_child.self_delete(request.session)

        unchanged_children = [acc_child for acc_child in accordion_children_after_edit[duplicated_card]
                              if acc_child not in added_accordion_children]

        added_children_html = ""
        for added_accordion_child in added_accordion_children:
            added_children_html += render_to_string(
                f"model_builder/object_cards/{added_accordion_child.template_name}_card.html",
                {added_accordion_child.template_name: added_accordion_child})

        if unchanged_children and added_accordion_children:
            last_unchanged_child = unchanged_children[-1]
            data_attribute_updates += last_unchanged_child.data_attributes_as_list_of_dict
            response_html += (f"<div hx-swap-oob='afterend:#{last_unchanged_child.web_id}'>"
                                  f"{added_children_html}</div>")

        elif added_accordion_children and not unchanged_children:
            response_html += (f"<div hx-swap-oob='beforeend:#flush-{duplicated_card.web_id} "
                              f".accordion-body'>{added_children_html}</div>")

    for duplicated_card in edited_obj.duplicated_cards:
        data_attribute_updates += duplicated_card.data_attributes_as_list_of_dict
        for parent in duplicated_card.all_accordion_parents:
            data_attribute_updates += parent.data_attributes_as_list_of_dict

    top_parent_ids = list(set([duplicated_card.top_parent.web_id for duplicated_card in
                                   edited_obj.duplicated_cards]))

    return response_html, ids_of_web_elements_with_lines_to_remove, data_attribute_updates, top_parent_ids


def generate_http_response_from_edit_html_and_events(
    response_html, ids_of_web_elements_with_lines_to_remove, data_attribute_updates, top_parent_ids):
    http_response = HttpResponse(response_html)

    http_response["HX-Trigger"] = json.dumps({
        "removeLinesAndUpdateDataAttributes": {
            "elementIdsOfLinesToRemove": ids_of_web_elements_with_lines_to_remove,
            "dataAttributeUpdates": data_attribute_updates
        }
    })

    http_response["HX-Trigger-After-Swap"] = json.dumps({
        "updateTopParentLines": {
            "topParentIds": top_parent_ids
        },
        "closePanelAfterSwap": True
    })

    return http_response


def edit_object(request, object_id, model_web=None):
    try:
        response_html, ids_of_web_elements_with_lines_to_remove, data_attribute_updates, top_parent_ids = (
            compute_edit_object_html_and_event_response(request, object_id, model_web))
    except Exception as e:
        return render_exception_modal(request, e)

    return generate_http_response_from_edit_html_and_events(
        response_html, ids_of_web_elements_with_lines_to_remove, data_attribute_updates, top_parent_ids)
