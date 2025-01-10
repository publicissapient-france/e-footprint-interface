# Important to keep these imports because they constitute the globals() dict
from efootprint.builders.hardware.servers_boaviztapi import get_cloud_server, on_premise_server_from_config
from efootprint.core.system import System
from efootprint.core.hardware.storage import Storage
from efootprint.core.hardware.servers.autoscaling import Autoscaling
from efootprint.core.hardware.servers.serverless import Serverless
from efootprint.core.hardware.servers.on_premise import OnPremise
from efootprint.core.hardware.hardware_base_classes import Hardware
from efootprint.core.usage.usage_pattern import UsagePattern
from efootprint.core.usage.user_journey import UserJourney
from efootprint.core.usage.user_journey import UserJourneyStep
from efootprint.core.usage.job import Job
from efootprint.core.hardware.network import Network
from efootprint.constants.countries import Country
from efootprint.abstract_modeling_classes.source_objects import SourceValue, Sources, SourceHourlyValues
from efootprint.constants.units import u
from efootprint.logger import logger
from model_builder.modeling_objects_web import ModelingObjectWeb, wrap_efootprint_object
from model_builder.model_web import ModelWeb


def create_efootprint_obj_from_post_data(request, model_web: ModelWeb, object_type: str):
    new_efootprint_obj_class = globals()[object_type]
    new_efootprint_obj = new_efootprint_obj_class.__new__(new_efootprint_obj_class)

    obj_creation_kwargs = {}
    obj_structure = model_web.get_object_structure(object_type)
    obj_creation_kwargs["name"] = request.POST["form_add_name"]

    for attr_dict in obj_structure.numerical_attributes:
        obj_creation_kwargs[attr_dict["attr_name"]] = SourceValue(
            float(request.POST.getlist(f'form_add_{attr_dict["attr_name"]}')[0]) * u(attr_dict["unit"]))

    for attr_dict in obj_structure.hourly_quantities_attributes:
        obj_creation_kwargs[attr_dict["attr_name"]] = SourceHourlyValues(
            float(request.POST.getlist(f'form_add_{attr_dict["attr_name"]}')[0]) * u(attr_dict["unit"]))

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


def add_new_object_to_system_from_builder(request, model_web: ModelWeb, object_type: str):
    if object_type in ["Autoscaling", "Serverless"]:
        new_efootprint_obj = get_cloud_server(request.POST.get('form_add_provider'), request.POST.get(
            'form_add_configuration'), SourceValue(int(request.POST['form_add_average_carbon_intensity'])* u.g / u.kWh))
    elif object_type == "OnPremise":
        new_efootprint_obj = on_premise_server_from_config(
            request.POST['form_add_name'],
            request.POST['form_add_nb_of_cpu_units'],
            request.POST['form_add_nb_of_cores_per_cpu_unit'],
            request.POST['form_add_nb_of_ram_units'],
            request.POST['form_add_ram_quantity_per_unit_in_gb'],
            SourceValue(int(request.POST['form_add_average_carbon_intensity'])* u.g / u.kWh)
        )
    else:
        raise PermissionError(f"Object type {object_type} not supported yet")
    new_efootprint_obj.name = request.POST.get('form_add_name')

    new_obj_wrapped = add_new_efootprint_object_to_system(request, model_web, new_efootprint_obj)

    return new_obj_wrapped


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
