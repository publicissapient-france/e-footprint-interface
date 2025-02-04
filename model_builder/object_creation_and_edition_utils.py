import os
from datetime import datetime

from django.contrib.sessions.backends.base import SessionBase
from django.shortcuts import render
from efootprint.builders.time_builders import create_hourly_usage_df_from_list
from efootprint.abstract_modeling_classes.source_objects import SourceValue, Sources, SourceHourlyValues, SourceObject
from efootprint.constants.units import u
from efootprint.logger import logger

from model_builder.modeling_objects_web import ModelingObjectWeb, wrap_efootprint_object
from model_builder.model_web import ModelWeb
from model_builder.class_structure import MODELING_OBJECT_CLASSES_DICT, efootprint_class_structure


def create_efootprint_obj_from_post_data(request, model_web: ModelWeb, object_type: str):
    new_efootprint_obj_class = MODELING_OBJECT_CLASSES_DICT[object_type]

    obj_creation_kwargs = {}
    obj_structure = efootprint_class_structure(object_type)
    obj_creation_kwargs["name"] = request.POST["form_add_name"]

    for attr_dict in obj_structure["numerical_attributes"]:
        attr_value_in_list = request.POST.getlist(f'form_add_{attr_dict["attr_name"]}')
        if not attr_value_in_list:
            logger.info(f"No value for {attr_dict['attr_name']} in {object_type} form. "
                        f"Default value {new_efootprint_obj_class.default_values()[attr_dict['attr_name']]} "
                        f"will be used.")
        else:
            obj_creation_kwargs[attr_dict["attr_name"]] = SourceValue(
                float(attr_value_in_list[0]) * u(attr_dict["unit"]))

    for attr_dict in obj_structure["hourly_quantities_attributes"]:
        obj_creation_kwargs[attr_dict["attr_name"]] = SourceHourlyValues(
            # Create hourly_usage_journey_starts from request.POST with the startDate and values
            create_hourly_usage_df_from_list(
                [float(value) for value
                 in request.POST.getlist(f'form_add_list_{attr_dict["attr_name"]}')[0].split(",")],
                start_date=datetime.strptime(
                    request.POST[f'form_add_date_{attr_dict["attr_name"]}'], "%Y-%m-%d"),
                pint_unit=u.dimensionless
            )
        )

    for str_attr in obj_structure["str_attributes"] + obj_structure["conditional_str_attributes"]:
        str_attr_name = str_attr["attr_name"]
        if f'form_add_{str_attr_name}' not in request.POST.keys():
            logger.info(f"No value for {str_attr_name} in {object_type} form. "
                        f"Default value {new_efootprint_obj_class.default_values()[str_attr_name]} will be used.")
        else:
            obj_creation_kwargs[str_attr_name] = SourceObject(
                request.POST[f'form_add_{str_attr_name}'], source=Sources.USER_DATA)

    for mod_obj in obj_structure["modeling_obj_attributes"]:
        new_mod_obj_id = request.POST[f'form_add_{mod_obj["attr_name"]}']
        obj_to_add = model_web.get_efootprint_object_from_efootprint_id(
            new_mod_obj_id, mod_obj["object_type"], request.session)
        obj_creation_kwargs[mod_obj["attr_name"]] = obj_to_add

    for mod_obj in obj_structure["list_attributes"]:
        obj_creation_kwargs[mod_obj["attr_name"]] = [
            model_web.get_efootprint_object_from_efootprint_id(obj_id, mod_obj["object_type"], request.session)
            for obj_id in request.POST.getlist(f'form_add_{mod_obj["attr_name"]}')]

    new_efootprint_obj = new_efootprint_obj_class.from_defaults(**obj_creation_kwargs)

    return new_efootprint_obj

def add_new_efootprint_object_to_system(request_session: SessionBase, model_web: ModelWeb, efootprint_object):
    object_type = efootprint_object.class_as_simple_str

    if object_type not in request_session["system_data"]:
        request_session["system_data"][object_type] = {}
        model_web.response_objs[object_type] = {}
    request_session["system_data"][object_type][efootprint_object.id] = efootprint_object.to_json()
    # Here we updated a sub dict of request.session so we have to explicitly tell Django that it has been updated
    request_session.modified = True

    model_web.response_objs[object_type][efootprint_object.id] = efootprint_object
    model_web.flat_efootprint_objs_dict[efootprint_object.id] = efootprint_object

    return wrap_efootprint_object(efootprint_object, model_web)


def edit_object_in_system(request, obj_to_edit: ModelingObjectWeb):
    model_web = obj_to_edit.model_web
    obj_structure = obj_to_edit.generate_structure()

    obj_to_edit.set_efootprint_value("name", request.POST["form_edit_name"])

    for attr_dict in obj_structure["numerical_attributes"]:
        if "form_edit_" + attr_dict["attr_name"] in request.POST.keys():
            request_unit = attr_dict["unit"]
            request_value = request.POST["form_edit_" + attr_dict["attr_name"]]
            new_value = SourceValue(float(request_value) * u(request_unit), Sources.USER_DATA)
            current_value = getattr(obj_to_edit, attr_dict["attr_name"])
            if new_value.value != current_value.value:
                logger.debug(f"{attr_dict['attr_name']} has changed in {obj_to_edit.efootprint_id}")
                new_value.set_label(current_value.label)
                obj_to_edit.set_efootprint_value(attr_dict["attr_name"], new_value)
    for attr_dict in obj_structure["str_attributes"] + obj_structure["conditional_str_attributes"]:
        if "form_edit_" + attr_dict["attr_name"] in request.POST.keys():
            new_value = SourceObject(request.POST["form_edit_" + attr_dict["attr_name"]], source=Sources.USER_DATA)
            current_value = getattr(obj_to_edit, attr_dict["attr_name"])
            if new_value.value != current_value.value:
                logger.debug(f"{attr_dict['attr_name']} has changed in {obj_to_edit.efootprint_id}")
                new_value.set_label(current_value.label)
                obj_to_edit.set_efootprint_value(attr_dict["attr_name"], new_value)
    for mod_obj in obj_structure["modeling_obj_attributes"]:
        if "form_edit_" + mod_obj["attr_name"] in request.POST.keys():
            new_mod_obj_id = request.POST["form_edit_" + mod_obj["attr_name"]]
            current_mod_obj_id = getattr(obj_to_edit, mod_obj["attr_name"]).efootprint_id
            if new_mod_obj_id != current_mod_obj_id:
                logger.debug(f"{mod_obj['attr_name']} has changed in {obj_to_edit.efootprint_id}")
                obj_to_add = model_web.get_efootprint_object_from_efootprint_id(
                    new_mod_obj_id, mod_obj["object_type"], request.session)
                obj_to_edit.set_efootprint_value(mod_obj["attr_name"], obj_to_add)
    for mod_obj in obj_structure["list_attributes"]:
        if "form_edit_" + mod_obj["attr_name"] in request.POST.keys():
            new_mod_obj_ids = request.POST.getlist("form_edit_" +mod_obj["attr_name"])
            current_mod_obj_ids = [mod_obj.efootprint_id for mod_obj in getattr(obj_to_edit, mod_obj["attr_name"])]
            added_mod_obj_ids = [obj_id for obj_id in new_mod_obj_ids if obj_id not in current_mod_obj_ids]
            removed_mod_obj_ids = [obj_id for obj_id in current_mod_obj_ids if obj_id not in new_mod_obj_ids]
            logger.debug(f"{mod_obj['attr_name']} has changed in {obj_to_edit.efootprint_id}")
            unchanged_mod_obj_ids = [obj_id for obj_id in current_mod_obj_ids if obj_id not in removed_mod_obj_ids]
            if new_mod_obj_ids != current_mod_obj_ids:
                obj_to_edit.set_efootprint_value(
                    mod_obj["attr_name"],
                    [model_web.get_web_object_from_efootprint_id(obj_id).modeling_obj
                     for obj_id in unchanged_mod_obj_ids + added_mod_obj_ids])

    # Update session data
    request.session["system_data"][obj_to_edit.class_as_simple_str][obj_to_edit.efootprint_id] = obj_to_edit.to_json()
    # Here we updated a sub dict of request.session so we have to explicitly tell Django that it has been updated
    request.session.modified = True

    return obj_to_edit


def render_exception_modal(request, exception):
    if os.environ.get("RAISE_EXCEPTIONS"):
        raise exception
    http_response = render(request, "model_builder/modals/exception-modal.html", {
        "msg": exception})

    http_response["HX-Trigger-After-Swap"] = "openModalDialog"

    return http_response
