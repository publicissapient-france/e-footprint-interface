from inspect import signature
from typing import get_origin, List, get_args

from efootprint.abstract_modeling_classes.explainable_objects import ExplainableQuantity
from efootprint.abstract_modeling_classes.modeling_object import ModelingObject
from efootprint.core.all_classes_in_order import ALL_CLASSES_IN_CANONICAL_COMPUTATION_ORDER


modeling_object_classes_dict = {modeling_object_class.__name__: modeling_object_class
                                for modeling_object_class in ALL_CLASSES_IN_CANONICAL_COMPUTATION_ORDER}


def efootprint_class_structure(efootprint_class_str: str):
    efootprint_class = modeling_object_classes_dict[efootprint_class_str]
    structure = {
        "numerical_attributes": [],
        "modeling_obj_attributes": [],
        "list_attributes": [],
        "str_attributes": efootprint_class.list_values(),
        "conditional_str_attributes": efootprint_class.conditional_list_values()
    }
    init_sig_params = signature(efootprint_class.__init__).parameters
    for attr_name in init_sig_params.keys():
        annotation = init_sig_params[attr_name].annotation
        if get_origin(annotation):
            if get_origin(annotation) in (list, List):
                object_type = get_args(annotation)[0]
                structure["list_attributes"].append({"attr_name": attr_name, "object_type": object_type.__name__})
        elif issubclass(annotation, ExplainableQuantity):
            default_value = efootprint_class.default_value(attr_name).value
            structure["numerical_attributes"].append(
                {"attr_name": attr_name, "unit": f"{default_value.units:~P}",
                 "long_unit": str(default_value.units),
                 "default_value": round(default_value.magnitude, 2)})
        elif issubclass(annotation, ModelingObject):
            structure["modeling_obj_attributes"].append({"attr_name": attr_name, "object_type": annotation.__name__})

    return structure


def generate_object_creation_structure(available_efootprint_classes: list, header: str, attributes_to_skip = None):
    if attributes_to_skip is None:
        attributes_to_skip = []

    efootprint_classes_dict = {"str_attributes": ["name"], "switch_item": "type_object_available"}
    type_efootprint_classes_available = {
        "category": "efootprint_classes_available",
        "header": header,
        "class": "",
        "fields": [{
            "input_type": "select",
            "id": "type_object_available",
            "name": "type_object_available",
            "required": True,
            "options": [{"label": service.__name__, "value": service.__name__}
                        for service in available_efootprint_classes]
        }
        ]
    }

    efootprint_classes_dict["items"] = [type_efootprint_classes_available]
    efootprint_classes_dict["dynamic_lists"] = []

    for index, efootprint_class in enumerate(available_efootprint_classes):
        class_fields = []
        class_structure = efootprint_class_structure(efootprint_class.__name__)
        for str_attribute, str_attribute_values in class_structure["str_attributes"].items():
            if str_attribute in attributes_to_skip:
                continue
            class_fields.append({
                "input_type": "select",
                "id": str_attribute,
                "name": str_attribute,
                "required": True,
                "options": [{"label": str(attr_value), "value": str(attr_value)} for attr_value in str_attribute_values]
            })
        for conditional_str_attribute, conditional_str_attribute_value \
            in class_structure["conditional_str_attributes"].items():
            if conditional_str_attribute in attributes_to_skip:
                continue
            class_fields.append({
                "input_type": "datalist",
                "id": conditional_str_attribute,
                "name": conditional_str_attribute,
                "options": None
            })
            efootprint_classes_dict["dynamic_lists"].append(
                {
                    "input": conditional_str_attribute,
                    "filter_by": conditional_str_attribute_value["depends_on"],
                    "list_value": {
                        str(conditional_value): [str(possible_value) for possible_value in possible_values]
                        for conditional_value, possible_values
                        in conditional_str_attribute_value["conditional_list_values"].items()
                    }
                })
        for numerical_attribute in class_structure["numerical_attributes"]:
            if numerical_attribute["attr_name"] in attributes_to_skip:
                continue
            class_fields.append({
                "input_type": "input",
                "id": numerical_attribute["attr_name"],
                "name": numerical_attribute["attr_name"],
                "unit": numerical_attribute["unit"],
                "required": True,
                "default": numerical_attribute["default_value"]
            })

        service_class = "d-none"
        if index == 0:
            service_class = ""
        efootprint_classes_dict["items"].append({
            "category": efootprint_class.__name__,
            "header": f"{efootprint_class.__name__} creation",
            "class": service_class,
            "fields": class_fields})

    return efootprint_classes_dict
