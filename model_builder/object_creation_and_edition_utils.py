from datetime import datetime

from efootprint.builders.time_builders import create_hourly_usage_df_from_list
from efootprint.core.usage.usage_pattern import UsagePattern
from efootprint.abstract_modeling_classes.source_objects import SourceValue, Sources, SourceHourlyValues
from efootprint.constants.units import u
from efootprint.logger import logger

from model_builder.modeling_objects_web import ModelingObjectWeb, wrap_efootprint_object
from model_builder.model_web import ModelWeb
from model_builder.class_structure import modeling_object_classes_dict


def create_efootprint_obj_from_post_data(request, model_web: ModelWeb, object_type: str):
    new_efootprint_obj_class = modeling_object_classes_dict[object_type]
    new_efootprint_obj = new_efootprint_obj_class.__new__(new_efootprint_obj_class)

    obj_creation_kwargs = {}
    obj_structure = model_web.get_object_structure(object_type)
    obj_creation_kwargs["name"] = request.POST["form_add_name"]

    for attr_dict in obj_structure.numerical_attributes:
        obj_creation_kwargs[attr_dict["attr_name"]] = SourceValue(
            float(request.POST.getlist(f'form_add_{attr_dict["attr_name"]}')[0]) * u(attr_dict["unit"]))

    for attr_dict in obj_structure.hourly_quantities_attributes:
        obj_creation_kwargs[attr_dict["attr_name"]] = SourceHourlyValues(
            #create hourly_user_journey_starts from request.POST with the startDate and index increment hourly and
            # the list of value
            create_hourly_usage_df_from_list(
                [float(value) for value in request.POST.getlist(f'form_add_list_{attr_dict["attr_name"]}')],
                start_date=datetime.strptime(request.POST[f'form_add_date_{attr_dict["attr_name"]}'], "%Y-%m-%d "
                                                                                                    "%H:%M:%S"),
                pint_unit=u.dimensionless
            )
            #float(request.POST.getlist(f'form_add_{attr_dict["attr_name"]}')[0]) * u(attr_dict["unit"])
        )

    for mod_obj in obj_structure.modeling_obj_attributes:
        new_mod_obj_id = request.POST[f'form_add_{mod_obj["attr_name"]}']
        obj_to_add = model_web.get_efootprint_object_from_efootprint_id(
            new_mod_obj_id, mod_obj["object_type"], request.session)
        obj_creation_kwargs[mod_obj["attr_name"]] = obj_to_add

    for mod_obj in obj_structure.list_attributes:
        obj_creation_kwargs[mod_obj["attr_name"]] = [
            model_web.flat_efootprint_objs_dict[obj_id]
            for obj_id in request.POST.getlist(f'form_add_{mod_obj["attr_name"]}')]

    new_efootprint_obj.__init__(**obj_creation_kwargs)

    return new_efootprint_obj

def create_new_usage_pattern_from_post_data(request, model_web: ModelWeb):
    user_journey = model_web.get_efootprint_object_from_efootprint_id(request.POST["form_add_user-journey"],
                                                                      "UserJourney", request.session)
    default_devices = model_web.get_efootprint_object_from_efootprint_id(request.POST["form_add_devices"],
                                                                         "Hardware", request.session)
    network = model_web.get_efootprint_object_from_efootprint_id(request.POST["form_add_network"], "Network",
                                                                 request.session)
    country = model_web.get_efootprint_object_from_efootprint_id(request.POST["form_add_country"], "Country",
                                                                    request.session)
    time_serie = SourceHourlyValues(
            create_hourly_usage_df_from_list(
                [float(value) for value in request.POST['form_add_list_hourly_user_journey_starts'].split(',')],
                start_date=datetime.strptime(
                    request.POST['form_add_date_hourly_user_journey_starts'],
                    "%Y-%m-%d"),
                pint_unit=u.dimensionless
            )
        )
    new_usage_pattern = UsagePattern(request.POST["form_add_name"], user_journey, [default_devices], network, country,
                                     time_serie)
    return new_usage_pattern

def add_new_efootprint_object_to_system(request, model_web: ModelWeb, efootprint_object):
    object_type = efootprint_object.class_as_simple_str

    if object_type not in request.session["system_data"]:
        request.session["system_data"][object_type] = {}
        model_web.response_objs[object_type] = {}
    request.session["system_data"][object_type][efootprint_object.id] = efootprint_object.to_json()
    # Here we updated a sub dict of request.session so we have to explicitly tell Django that it has been updated
    request.session.modified = True

    model_web.response_objs[object_type][efootprint_object.id] = efootprint_object
    model_web.flat_efootprint_objs_dict[efootprint_object.id] = efootprint_object

    return wrap_efootprint_object(efootprint_object, model_web)


def edit_object_in_system(request, obj_to_edit: ModelingObjectWeb):
    model_web = obj_to_edit.model_web
    obj_structure = obj_to_edit.structure

    obj_to_edit.set_efootprint_value("name", request.POST["form_edit_name"])

    for attr_dict in obj_structure.numerical_attributes:
        request_unit = attr_dict["unit"]
        request_value = request.POST.getlist("form_edit_" + attr_dict["attr_name"])[0]
        new_value = SourceValue(float(request_value) * u(request_unit), Sources.USER_DATA)
        current_value = getattr(obj_to_edit, attr_dict["attr_name"])
        if new_value.value != current_value.value:
            logger.debug(f"{attr_dict['attr_name']} has changed in {obj_to_edit.efootprint_id}")
            new_value.set_label(current_value.label)
            obj_to_edit.set_efootprint_value(attr_dict["attr_name"], new_value)
    for mod_obj in obj_structure.modeling_obj_attributes:
        new_mod_obj_id = request.POST["form_edit_" + mod_obj["attr_name"]]
        current_mod_obj_id = getattr(obj_to_edit, mod_obj["attr_name"]).efootprint_id
        if new_mod_obj_id != current_mod_obj_id:
            logger.debug(f"{mod_obj['attr_name']} has changed in {obj_to_edit.efootprint_id}")
            obj_to_add = model_web.get_efootprint_object_from_efootprint_id(
                new_mod_obj_id, mod_obj["object_type"], request.session)
            obj_to_edit.set_efootprint_value(mod_obj["attr_name"], obj_to_add)
    for mod_obj in obj_structure.list_attributes:
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
