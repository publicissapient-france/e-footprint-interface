import json

from django.http import HttpResponse
from django.shortcuts import render
from efootprint.logger import logger

from model_builder.class_structure import efootprint_class_structure
from model_builder.model_web import ModelWeb
from model_builder.modeling_objects_web import JobWeb, UsageJourneyStepWeb, UsagePatternWeb
from model_builder.views_edition import compute_edit_object_html_and_event_response, \
    generate_http_response_from_edit_html_and_events


def ask_delete_object(request, object_id):
    model_web = ModelWeb(request.session, launch_system_computations=False)
    model_web.set_all_trigger_modeling_updates_to_false()
    web_obj = model_web.get_web_object_from_efootprint_id(object_id)

    if (not (isinstance(web_obj, UsagePatternWeb) or isinstance(web_obj, JobWeb)
             or isinstance(web_obj, UsageJourneyStepWeb)) and web_obj.modeling_obj_containers):

        http_response = render(request, "model_builder/modals/cant-delete-modal.html",
            context={"msg":f"Can’t delete {web_obj.name} because it is referenced by "
                           f"{[obj.efootprint_id for obj in web_obj.modeling_obj_containers]}"})
    else:
        message = f"Are you sure you want to delete this {web_obj.class_as_simple_str} ?"
        sub_message = ""
        remove_card_with_hyperscript = True
        if isinstance(web_obj, JobWeb) or isinstance(web_obj, UsageJourneyStepWeb):
            remove_card_with_hyperscript = False
            if len(web_obj.duplicated_cards) > 1:
                message = (f"This {web_obj.class_as_simple_str} is mirrored {len(web_obj.duplicated_cards)} times, "
                           f"this action will delete all mirrored {web_obj.class_as_simple_str}s.")
                sub_message = f"To delete only one {web_obj.class_as_simple_str}, break the mirroring link first."

        http_response = render(
            request, "model_builder/modals/delete-card-modal.html",
            context={"obj": web_obj, "message": message, "sub_message": sub_message,
                     "remove_card_with_hyperscript": remove_card_with_hyperscript})

    http_response["HX-Trigger-After-Swap"] = "openModalDialog"
    return http_response


def delete_object(request, object_id):
    model_web = ModelWeb(request.session, launch_system_computations=False)
    model_web.set_all_trigger_modeling_updates_to_false()

    web_obj = model_web.get_web_object_from_efootprint_id(object_id)
    obj_type = web_obj.class_as_simple_str
    system = model_web.system

    elements_with_lines_to_remove = []

    http_response = HttpResponse(status=204)

    if obj_type == "UsagePattern":
        new_up_list = [up for up in system.get_efootprint_value("usage_patterns") if up.id != object_id]
        system.set_efootprint_value("usage_patterns", new_up_list)
        request.session["system_data"]["System"]["uuid-system-1"]["usage_patterns"] = [up.id for up in new_up_list]
        request.session["system_data"]["UsagePattern"].pop(object_id)
        if len(new_up_list) == 0:
            del request.session["system_data"]["UsagePattern"]
        request.session.modified = True
        elements_with_lines_to_remove.append(object_id)
    elif isinstance(web_obj, JobWeb) or isinstance(web_obj, UsageJourneyStepWeb):
        response_html = ""
        ids_of_web_elements_with_lines_to_remove, data_attribute_updates, top_parent_ids = [], [], []
        for duplicated_card in web_obj.duplicated_cards:
            mutable_post = request.POST.copy()
            for key in list(mutable_post.keys()):
                if key.startswith('form_add'):
                    del mutable_post[key]
            parent = duplicated_card.accordion_parent
            logger.info(f"Removing {duplicated_card.name} from {parent.name}")
            mutable_post['form_edit_name'] = parent.name
            new_list_attribute_ids = [list_attribute.efootprint_id for list_attribute in parent.accordion_children
                                      if list_attribute.efootprint_id != duplicated_card.efootprint_id]
            list_attribute_name = efootprint_class_structure(
                parent.class_as_simple_str)["list_attributes"][0]["attr_name"]
            mutable_post.setlist(f'form_edit_{list_attribute_name}', new_list_attribute_ids)
            request.POST = mutable_post
            (partial_response_html, partial_ids_of_web_elements_with_lines_to_remove,
             partial_data_attribute_updates, partial_top_parent_ids) = compute_edit_object_html_and_event_response(
                request, parent.efootprint_id, model_web)
            response_html += partial_response_html
            ids_of_web_elements_with_lines_to_remove += partial_ids_of_web_elements_with_lines_to_remove
            data_attribute_updates += partial_data_attribute_updates
            top_parent_ids += partial_top_parent_ids

            http_response = generate_http_response_from_edit_html_and_events(
                response_html, ids_of_web_elements_with_lines_to_remove, data_attribute_updates, top_parent_ids)
    else:
        web_obj.self_delete(request.session)
        elements_with_lines_to_remove.append(object_id)

    if elements_with_lines_to_remove:
        http_response["HX-Trigger"] = json.dumps({
            "removeLinesAndUpdateDataAttributes": {
                "elementIdsOfLinesToRemove": elements_with_lines_to_remove,
                "dataAttributeUpdates": []
            }
        })

    return http_response
