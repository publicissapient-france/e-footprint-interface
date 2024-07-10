from efootprint.constants.countries import Country
from efootprint.core.system import System

from django.template.loader import render_to_string


def modeling_obj_containers_excluding_class(efootprint_obj, class_to_exclude):
    return [elt for elt in efootprint_obj.modeling_obj_containers if not isinstance(elt, class_to_exclude)]


def create_drawflow_node_data(obj_data, efootprint_ids_to_int_ids_map):
    index = efootprint_ids_to_int_ids_map[obj_data["object"].id]
    input_connections = {}
    if modeling_obj_containers_excluding_class(obj_data["object"], System):
        input_connections["input_1"] = {"connections": [
            {"node": efootprint_ids_to_int_ids_map[obj.id], "input": "output_1"}
            for obj in modeling_obj_containers_excluding_class(obj_data["object"], System)]}
    output_connections = {}
    if obj_data["modeling_obj_attributes"] or obj_data["list_attributes"]:
        output_connections["output_1"] = {"connections": [
            {"node": efootprint_ids_to_int_ids_map[obj.id], "output": "input_1"}
            for obj in obj_data["modeling_obj_attributes"] + obj_data["list_attributes"]
            if not isinstance(obj, Country)]}
    efootprint_class = obj_data["object"].class_as_simple_str

    return {
        "id": index, "name": efootprint_class, "class": f"!bg-{efootprint_class}",
        "data": obj_data["object"].to_json(),
        "html": render_to_string("model_builder/object-card.html",
                                 {"object": obj_data, "object_type": efootprint_class}),
        "typenode": False,
        "inputs": input_connections, "outputs": output_connections}
