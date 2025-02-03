from django.http import HttpResponse, QueryDict
from django.shortcuts import render
from efootprint.api_utils.system_to_json import system_to_json

from model_builder.model_web import ModelWeb
from model_builder.modeling_objects_web import JobWeb, UsageJourneyStepWeb


def ask_delete_object(request, object_id):
    model_web = ModelWeb(request.session, launch_system_computations=False)
    model_web.set_all_trigger_modeling_updates_to_false()
    web_obj = model_web.get_web_object_from_efootprint_id(object_id)
    obj_type = web_obj.class_as_simple_str

    if obj_type != "UsagePattern" and web_obj.modeling_obj_containers:
        return render(
            request, "model_builder/modals/cant-delete-modal.html",
            context={"msg":f"Can’t delete {web_obj.name} because it is referenced by "
                           f"{[obj.efootprint_id for obj in web_obj.modeling_obj_containers]}"})
    else:
        if isinstance(web_obj, JobWeb):
            request.POST = QueryDict()
        else:
            return render(
                request, "model_builder/modals/delete-card-modal.html", context={"obj": web_obj})


def delete_object(request, object_id):
    model_web = ModelWeb(request.session, launch_system_computations=False)
    model_web.set_all_trigger_modeling_updates_to_false()

    web_obj = model_web.get_web_object_from_efootprint_id(object_id)
    obj_type = web_obj.class_as_simple_str
    system = model_web.system

    if obj_type == "UsagePattern":
        system.set_efootprint_value("usage_patterns",
                                    [up for up in system.get_efootprint_value("usage_patterns") if up.id != object_id])

    web_obj.self_delete()

    request.session["system_data"] = system_to_json(system.modeling_obj, save_calculated_attributes=False)

    http_response = HttpResponse(status=204)

    return http_response
