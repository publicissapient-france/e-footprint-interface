from efootprint.abstract_modeling_classes.explainable_objects import ExplainableQuantity
from efootprint.abstract_modeling_classes.modeling_object import ModelingObject
from efootprint.api_utils.json_to_system import json_to_system
from model_builder.views import retrieve_attributes_by_type

import json
import inspect
import os


with open("default_system_data.json", "r") as file:
    json_data = json.load(file)

efootprint_obj_structure = {}
response_objs, flat_obj_dict = json_to_system(json_data)

for efootprint_object_type in response_objs.keys():
    first_efootprint_obj = list(response_objs[efootprint_object_type].values())[0]
    efootprint_class_init = first_efootprint_obj.__class__.__init__
    init_param_names = [param.name for param in inspect.signature(efootprint_class_init).parameters.values()]
    efootprint_obj_structure[efootprint_object_type] = {
        "numerical_attributes": [
            {"attr_name": attr_name_value_pair[0], "unit": f"{attr_name_value_pair[1].value.units:~P}",
             "long_unit": str(attr_name_value_pair[1].value.units),
             "default_value": round(attr_name_value_pair[1].value.magnitude, 2)}
            for attr_name_value_pair in retrieve_attributes_by_type(first_efootprint_obj, ExplainableQuantity)
            if attr_name_value_pair[0] in init_param_names],
        "modeling_obj_attributes": [
            {"attr_name": attr_name_value_pair[0], "object_type": attr_name_value_pair[1].class_as_simple_str}
            for attr_name_value_pair in retrieve_attributes_by_type(first_efootprint_obj, ModelingObject)
        ],
        "list_attributes": [
            {"attr_name": attr_name_value_pair[0], "object_type": attr_name_value_pair[1][0].class_as_simple_str}
            for attr_name_value_pair in retrieve_attributes_by_type(first_efootprint_obj, list)]
    }


with open(os.path.join("..", 'theme', 'static', "object_inputs_and_default_values.json"), "w") as file:
    json.dump(efootprint_obj_structure, file, indent=4)
