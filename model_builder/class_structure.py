from inspect import signature
from typing import get_origin, List, get_args

from efootprint.abstract_modeling_classes.explainable_objects import ExplainableQuantity, ExplainableHourlyQuantities
from efootprint.abstract_modeling_classes.modeling_object import ModelingObject
from efootprint.core.all_classes_in_order import ALL_CLASSES_IN_CANONICAL_COMPUTATION_ORDER


MODELING_OBJECT_CLASSES_DICT = {modeling_object_class.__name__: modeling_object_class
                                for modeling_object_class in ALL_CLASSES_IN_CANONICAL_COMPUTATION_ORDER}


def efootprint_class_structure(efootprint_class_str: str):
    efootprint_class = MODELING_OBJECT_CLASSES_DICT[efootprint_class_str]
    structure = {
        "numerical_attributes": [],
        "hourly_quantities_attributes": [],
        "modeling_obj_attributes": [],
        "list_attributes": [],
        "str_attributes": [{"attr_name": key, "list_values": [str(value) for value in values]}
                           for key, values in efootprint_class.list_values().items()],
        "conditional_str_attributes": [
            {
                "attr_name": key,
                "depends_on": value["depends_on"],
                "conditional_list_values": {
                    str(conditional_value): [str(possible_value) for possible_value in possible_values]
                    for conditional_value, possible_values in value["conditional_list_values"].items()
                }
            }
            for key, value in efootprint_class.conditional_list_values().items()]
    }
    efootprint_class_default_values = efootprint_class.default_values()
    init_sig_params = signature(efootprint_class.__init__).parameters
    for attr_name in init_sig_params.keys():
        annotation = init_sig_params[attr_name].annotation
        if get_origin(annotation):
            if get_origin(annotation) in (list, List):
                object_type = get_args(annotation)[0]
                structure["list_attributes"].append({"attr_name": attr_name, "object_type": object_type.__name__})
        elif issubclass(annotation, ExplainableQuantity):
            default_value = efootprint_class_default_values[attr_name].value
            structure["numerical_attributes"].append(
                {"attr_name": attr_name, "unit": f"{default_value.units:~P}",
                 "long_unit": str(default_value.units),
                 "default_value": round(default_value.magnitude, 2)})
        elif issubclass(annotation, ExplainableHourlyQuantities):
            structure["hourly_quantities_attributes"].append({"attr_name": attr_name})
        elif issubclass(annotation, ModelingObject):
            structure["modeling_obj_attributes"].append({"attr_name": attr_name, "object_type": annotation.__name__})

    return structure


def generate_object_creation_structure(available_efootprint_classes: list, header: str, attributes_to_skip = None):
    if attributes_to_skip is None:
        attributes_to_skip = []

    dynamic_form_dict = {
        "switch_item": "type_object_available",
        "switch_values": [available_class.__name__ for available_class in available_efootprint_classes],
        "dynamic_lists": []}

    type_efootprint_classes_available = {
        "category": "efootprint_classes_available",
        "header": header,
        "class": "",
        "fields": [{
            "input_type": "select",
            "id": "type_object_available",
            "name": "type_object_available",
            "options": [{"label": available_class.__name__, "value": available_class.__name__}
                        for available_class in available_efootprint_classes]
        }
        ]
    }

    structure_dict = {"items": [type_efootprint_classes_available]}

    for index, efootprint_class in enumerate(available_efootprint_classes):
        class_structure = efootprint_class_structure(efootprint_class.__name__)
        class_fields, dynamic_lists = format_structure_for_dynamic_form(class_structure, attributes_to_skip)

        if dynamic_lists:
            dynamic_form_dict["dynamic_lists"].extend(
                [elt for elt in dynamic_lists
                 if elt["input"] not in [elt["input"] for elt in dynamic_form_dict["dynamic_lists"]]])


        structure_dict["items"].append({
            "category": efootprint_class.__name__,
            "header": f"{efootprint_class.__name__} creation",
            "fields": class_fields})

    return structure_dict, dynamic_form_dict


def generate_object_edition_structure(web_object, attributes_to_skip=None):
    if attributes_to_skip is None:
        attributes_to_skip = []

    object_fields, dynamic_lists = format_structure_for_dynamic_form(
        web_object.generate_structure(), attributes_to_skip)

    return {"fields": object_fields}, {"dynamic_lists": dynamic_lists}


def format_structure_for_dynamic_form(input_structure, attributes_to_skip):
    structure_fields = []
    dynamic_lists = []

    for str_attribute_dict in input_structure["str_attributes"]:
        if str_attribute_dict["attr_name"] in attributes_to_skip:
            continue
        structure_fields.append({
            "input_type": "select",
            "id": str_attribute_dict["attr_name"],
            "name": str_attribute_dict["attr_name"],
            "selected": str_attribute_dict.get("attr_value", None),
            "options": [
                {"label": attr_value, "value": attr_value} for attr_value in str_attribute_dict["list_values"]]
        })
    for conditional_str_attribute_dict in input_structure["conditional_str_attributes"]:
        if conditional_str_attribute_dict["attr_name"] in attributes_to_skip:
            continue
        structure_fields.append({
            "input_type": "datalist",
            "id": conditional_str_attribute_dict["attr_name"],
            "name": conditional_str_attribute_dict["attr_name"],
            "selected": conditional_str_attribute_dict.get("attr_value", None),
            "options": None
        })
        dynamic_lists.append(
                {
                    "input": conditional_str_attribute_dict["attr_name"],
                    "filter_by": conditional_str_attribute_dict["depends_on"],
                    "list_value": conditional_str_attribute_dict["conditional_list_values"]
                })
    for numerical_attribute in input_structure["numerical_attributes"]:
        if numerical_attribute["attr_name"] in attributes_to_skip:
            continue
        structure_fields.append({
            "input_type": "input",
            "id": numerical_attribute["attr_name"],
            "name": numerical_attribute["attr_name"],
            "unit": numerical_attribute["unit"],
            "default": numerical_attribute.get("attr_value", numerical_attribute["default_value"])
        })

    return structure_fields, dynamic_lists
