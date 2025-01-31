from efootprint.abstract_modeling_classes.explainable_object_base_class import ExplainableObject
from efootprint.abstract_modeling_classes.explainable_objects import EmptyExplainableObject
from efootprint.abstract_modeling_classes.modeling_object import ModelingObject
from efootprint.core.usage.usage_pattern import UsagePattern


def retrieve_attributes_by_type(modeling_obj, attribute_type):
    output_list = []
    for attr_name, attr_value in vars(modeling_obj).items():
        if (isinstance(attr_value, attribute_type)
            and attr_name not in modeling_obj.attributes_that_shouldnt_trigger_update_logic):
            output_list.append({'attr_name': attr_name, 'attr_value': attr_value})

    return output_list

class EmptyExplainableObjectWeb:
    def __init__(self, attr_name):
        self.attr_name_in_mod_obj_container = attr_name

    @property
    def rounded_magnitude(self):
        return 0

    @property
    def short_unit(self):
        return ""

    @property
    def readable_attr_name(self):
        return self.attr_name_in_mod_obj_container.replace("_", " ")


class ExplainableObjectWeb:
    def __init__(self, explainable_quantity: ExplainableObject):
        self.explainable_quantity = explainable_quantity

    def __getattr__(self, name):
        attr = getattr(self.explainable_quantity, name)

        return attr

    @property
    def rounded_magnitude(self):
        return round(self.magnitude, 2)

    @property
    def short_unit(self):
        return f"{self.value.units:~P}"

    @property
    def readable_attr_name(self):
        return self.attr_name_in_mod_obj_container.replace("_", " ")


class ModelingObjectWeb:
    def __init__(self, modeling_obj: ModelingObject, model_web):
        self._modeling_obj = modeling_obj
        self.model_web = model_web
        self.structure = self.model_web.get_object_structure(self.class_as_simple_str)

    def __getattr__(self, name):
        attr = getattr(self._modeling_obj, name)

        if name == "id":
            raise ValueError("The id attribute shouldn’t be retrieved by ModelingObjectWrapper objects. "
                             "Use efootprint_id and web_id for clear disambiguation.")

        if isinstance(attr, EmptyExplainableObject):
            return EmptyExplainableObjectWeb(attr)

        if isinstance(attr, list) and len(attr) > 0 and isinstance(attr[0], ModelingObject):
            return [wrap_efootprint_object(item, self.model_web) for item in attr]

        if isinstance(attr, ModelingObject):
            return wrap_efootprint_object(attr, self.model_web)

        if isinstance(attr, ExplainableObject):
            return ExplainableObjectWeb(attr)

        return attr

    def __setattr__(self, key, value):
        if key in ["_modeling_obj", "model_web", "structure"]:
            super.__setattr__(self, key, value)
        elif key in self.structure.all_attribute_names + ["name", "id"]:
            raise PermissionError(f"{self} is trying to set the {key} attribute that is also an attribute of its "
                                  f"underlying e-footprint object.")
        else:
            super.__setattr__(self, key, value)

    def __hash__(self):
        return hash(self.web_id)

    def __eq__(self, other):
        return self.web_id == other.web_id

    def set_efootprint_value(self, key, value):
        error_message = (f"{self} tried to set a ModelingObjectWrapper attribute to its underlying e-footprint "
                         f"object, which is forbidden. Only set e-footprint objects as attributes of e-footprint "
                         f"objects.")
        if isinstance(value, list) and len(value) > 0 and isinstance(value[0], ModelingObjectWeb):
            raise PermissionError(error_message)

        if isinstance(value, ModelingObjectWeb):
            raise PermissionError(error_message)

        if isinstance(value, ExplainableObjectWeb):
            raise PermissionError(error_message)

        self._modeling_obj.__setattr__(key, value)

    @property
    def modeling_obj(self):
        return self._modeling_obj

    @property
    def efootprint_id(self):
        return self._modeling_obj.id

    @property
    def web_id(self):
        return self._modeling_obj.id

    @property
    def duplicated_cards(self):
        return [self]

    @property
    def template_name(self):
        return self.structure.template_name

    @property
    def links_to(self):
        return ""

    @property
    def data_line_opt(self):
        return "object-to-object"

    @property
    def data_attributes_as_list_of_dict(self):
        return [{'id': f'{self.web_id}', 'data-link-to': self.links_to, 'data-line-opt': self.data_line_opt}]

    @property
    def all_accordion_parents(self):
        list_parents = []
        parent = self.accordion_parent
        while parent:
            list_parents.append(parent)
            parent = parent.accordion_parent

        return list_parents

    @property
    def top_parent(self):
        if len(self.all_accordion_parents) == 0:
            return self
        else:
            return self.all_accordion_parents[-1]

    @property
    def numerical_attributes(self):
        numerical_attributes_from_structure = self.structure.numerical_attributes
        for numerical_attribute in numerical_attributes_from_structure:
            numerical_attribute["attr_value"] = getattr(self, numerical_attribute["attr_name"])

        return numerical_attributes_from_structure

    @property
    def mod_obj_attributes(self):
        efootprint_mod_obj_attributes = retrieve_attributes_by_type(self._modeling_obj, ModelingObject)
        for mod_obj_dict in efootprint_mod_obj_attributes:
            mod_obj_dict["existing_objects"] = self.model_web.get_web_objects_from_efootprint_type(
                mod_obj_dict["attr_value"].class_as_simple_str)
            mod_obj_dict["attr_value"] = wrap_efootprint_object(mod_obj_dict["attr_value"], self.model_web)

        return efootprint_mod_obj_attributes

    @property
    def list_attributes(self):
        attributes_from_structure = self.structure.list_attributes
        list_efootprint_mod_obj_attributes = retrieve_attributes_by_type(self._modeling_obj, list)
        for efootprint_mod_obj_attribute_dict in list_efootprint_mod_obj_attributes:
            # TODO: test that logic works in case e-footprint object has empty list attribute
            efootprint_mod_obj_attribute_dict["attr_value"] = [
                self.model_web.get_web_object_from_efootprint_id(efootprint_mod_obj.id)
                for efootprint_mod_obj in efootprint_mod_obj_attribute_dict["attr_value"]]
            list_attribute_object_type = [
                attribute["object_type"] for attribute in attributes_from_structure
                if attribute["attr_name"] == efootprint_mod_obj_attribute_dict["attr_name"]][0]
            efootprint_attribute_ids = [
                obj.efootprint_id for obj in efootprint_mod_obj_attribute_dict["attr_value"]]
            existing_web_objects_of_same_type_that_are_not_attributes = [
                obj for obj in self.model_web.get_web_objects_from_efootprint_type(list_attribute_object_type)
                if obj.efootprint_id not in efootprint_attribute_ids]
            efootprint_mod_obj_attribute_dict["existing_objects"] = (
                efootprint_mod_obj_attribute_dict["attr_value"]
                + existing_web_objects_of_same_type_that_are_not_attributes)

        return list_efootprint_mod_obj_attributes

    @property
    def is_deletable(self):
        is_deletable = False
        if not self._modeling_obj.modeling_obj_containers:
            is_deletable = True
        if isinstance(self._modeling_obj, UsagePattern) and len(self.model_web.system.usage_patterns) > 1:
            is_deletable = True

        return is_deletable

class ServerWeb(ModelingObjectWeb):
    @property
    def template_name(self):
        return "server"

    @property
    def accordion_parent(self):
        return None

    @property
    def accordion_children(self):
        return [self.storage]


class JobWeb(ModelingObjectWeb):
    @property
    def web_id(self):
        raise PermissionError(f"JobWeb objects don’t have a web_id attribute because their html "
                             f"representation should be managed by the DuplicatedJobWeb object")

    @property
    def duplicated_cards(self):
        duplicated_cards = []
        for usage_journey_step in self.usage_journey_steps:
            for duplicated_usage_journey_card in usage_journey_step.duplicated_cards:
                duplicated_cards.append(DuplicatedJobWeb(self._modeling_obj, duplicated_usage_journey_card))

        return duplicated_cards


class DuplicatedJobWeb(ModelingObjectWeb):
    def __init__(self, modeling_obj: ModelingObject, uj_step):
        super().__init__(modeling_obj, uj_step.model_web)
        self.usage_journey_step = uj_step

    @property
    def template_name(self):
        return "job"

    @property
    def web_id(self):
        return f"{self.usage_journey_step.web_id}_{self.efootprint_id}"

    @property
    def links_to(self):
        return self.server.web_id

    @property
    def accordion_parent(self):
        return self.usage_journey_step

    @property
    def accordion_children(self):
        return []

    @property
    def data_line_opt(self):
        return "object-to-object-inside-card"


class UsageJourneyStepWeb(ModelingObjectWeb):
    @property
    def web_id(self):
        raise PermissionError(f"UsageJourneyStepWeb objects don’t have a web_id attribute because their html "
                             f"representation should be managed by the DuplicatedUsageJourneyStepWeb object")

    @property
    def duplicated_cards(self):
        duplicated_cards = []
        for usage_journey in self.usage_journeys:
            duplicated_cards.append(DuplicatedUsageJourneyStepWeb(self._modeling_obj, usage_journey))

        return duplicated_cards

class DuplicatedUsageJourneyStepWeb(UsageJourneyStepWeb):
    def __init__(self, modeling_obj: ModelingObject, usage_journey):
        super().__init__(modeling_obj, usage_journey.model_web)
        self.usage_journey = usage_journey

    @property
    def web_id(self):
        return f"{self.usage_journey.web_id}_{self.efootprint_id}"

    @property
    def links_to(self):
        linked_server_ids = set([job.server.web_id for job in self.jobs])
        return "|".join(linked_server_ids)

    @property
    def accordion_parent(self):
        return self.usage_journey

    @property
    def accordion_children(self):
        return self.jobs

    @property
    def jobs(self):
        web_jobs = []
        for job in self._modeling_obj.jobs:
            web_jobs.append(DuplicatedJobWeb(job, self))

        return web_jobs

    @property
    def icon_links_to(self):
        usage_journey_steps = self.usage_journey.uj_steps
        index = usage_journey_steps.index(self)
        if index < len(usage_journey_steps) - 1:
            link_to = f"icon-{usage_journey_steps[index+1].web_id}"
        else:
            link_to = f'add-usage-pattern-{self.usage_journey.web_id}'

        return link_to

    @property
    def icon_leaderline_style(self):
        usage_journey_steps = self.usage_journey.uj_steps
        index = usage_journey_steps.index(self)
        if index < len(usage_journey_steps) - 1:
            class_name = "vertical-step-swimlane"
        else:
            class_name = 'step-dot-line'

        return class_name

    @property
    def data_line_opt(self):
        return "object-to-object-inside-card"

    @property
    def data_attributes_as_list_of_dict(self):
        data_attribute_updates = super().data_attributes_as_list_of_dict
        data_attribute_updates.append(
            {'id': f'icon-{self.web_id}', 'data-link-to': self.icon_links_to,
             'data-line-opt': self.icon_leaderline_style})

        return data_attribute_updates

class UsageJourneyWeb(ModelingObjectWeb):
    @property
    def links_to(self):
        linked_server_ids = set()
        for uj_step in self.uj_steps:
            for job in uj_step.jobs:
                linked_server_ids.add(job.server.web_id)

        return "|".join(sorted(linked_server_ids))

    @property
    def accordion_parent(self):
        return None

    @property
    def accordion_children(self):
        return self.uj_steps

    @property
    def uj_steps(self):
        web_uj_steps = []
        for uj_step in self._modeling_obj.uj_steps:
            web_uj_steps.append(DuplicatedUsageJourneyStepWeb(uj_step, self))

        return web_uj_steps


class UsagePatternWeb(ModelingObjectWeb):
    @property
    def links_to(self):
        return self.usage_journey.web_id

    @property
    def accordion_parent(self):
        return None

    @property
    def accordion_children(self):
        # TODO: Add Device mix Network mix and Country mix
        return []


wrapper_mapping = {
    # TODO: create a mapping for all classes
    "Server": ServerWeb,
    "GPUServer": ServerWeb,
    "UsageJourneyStep": UsageJourneyStepWeb,
    "UsageJourney": UsageJourneyWeb,
    "UsagePattern": UsagePatternWeb,
    "Job": JobWeb,
    "GenAIJob": JobWeb,
    "VideoStreamingJob": JobWeb,
    "WebApplicationJob": JobWeb,
}

def wrap_efootprint_object(modeling_obj, model_web):
    if modeling_obj.class_as_simple_str in wrapper_mapping.keys():
        return wrapper_mapping[modeling_obj.class_as_simple_str](modeling_obj, model_web)

    return ModelingObjectWeb(modeling_obj, model_web)
