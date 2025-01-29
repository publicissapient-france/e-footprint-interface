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
