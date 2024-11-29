from efootprint.abstract_modeling_classes.explainable_object_base_class import ExplainableObject
from efootprint.abstract_modeling_classes.explainable_objects import ExplainableQuantity, ExplainableHourlyQuantities
from efootprint.abstract_modeling_classes.modeling_object import ModelingObject, PREVIOUS_LIST_VALUE_SET_SUFFIX
from efootprint.core.usage.usage_pattern import UsagePattern


def retrieve_attributes_by_type(
    modeling_obj, attribute_type, attrs_to_ignore=['modeling_obj_containers', "all_changes"]):
    output_list = []
    for attr_name, attr_value in vars(modeling_obj).items():
        if (isinstance(attr_value, attribute_type) and attr_name not in attrs_to_ignore
                and PREVIOUS_LIST_VALUE_SET_SUFFIX not in attr_name):
            output_list.append((attr_name, attr_value))

    return output_list


class ExplainableObjectWeb:
    def __init__(self, explainable_quantity: ExplainableObject):
        self.explainable_quantity = explainable_quantity

    def __getattr__(self, name):
        attr = getattr(self._modeling_obj, name)

        return attr

    @property
    def short_unit(self):
        return f"{self.value.units:~P}"

    @property
    def readable_attr_name(self):
        return self.attr_name_in_mod_obj_container.replace("_", " ")


class ModelingObjectWrapper:
    def __init__(self, modeling_obj, model_web):
        self._modeling_obj = modeling_obj
        self.model_web = model_web

    def __getattr__(self, name):
        attr = getattr(self._modeling_obj, name)

        if isinstance(attr, list) and len(attr) > 0 and isinstance(attr[0], ModelingObject):
            return [wrap_efootprint_object(item, self.model_web) for item in attr]

        if isinstance(attr, ModelingObject):
            return wrap_efootprint_object(attr, self.model_web)

        if isinstance(attr, ExplainableObject):
            return ExplainableObjectWeb(attr)

        return attr

    @property
    def explainable_quantities(self):
        return retrieve_attributes_by_type(self, ExplainableQuantity)

    @property
    def explainable_hourly_quantities(self):
        return retrieve_attributes_by_type(self, ExplainableHourlyQuantities)

    @property
    def mod_obj_attributes(self):
        return retrieve_attributes_by_type(self, ModelingObject)

    @property
    def list_attributes(self):
        return retrieve_attributes_by_type(self, list)

    @property
    def is_deletable(self):
        is_deletable = False
        if not self._modeling_obj.modeling_obj_containers:
            is_deletable = True
        if isinstance(self._modeling_obj, UsagePattern) and len(self.model_web.system.usage_patterns) > 1:
            is_deletable = True

        return is_deletable


class JobWeb(ModelingObjectWrapper):
    @property
    def links_to(self):
        return self.server.id


class DuplicatedJobWeb(JobWeb):
    def __init__(self, modeling_obj, model_web, web_id, uj_step):
        super().__init__(modeling_obj, model_web)
        self.id = web_id
        self.user_journey_steps = uj_step


class UserJourneyStepWeb(ModelingObjectWrapper):
    @property
    def links_to(self):
        linked_server_ids = set([job.server.id for job in self.jobs])
        return "|".join(linked_server_ids)

    @property
    def jobs(self):
        web_jobs = []
        for job in self._modeling_obj.jobs:
            if len(job.user_journey_steps) == 1:
                job_id = job.id
            else:
                job_id = f"{job.id}_{self.id}"
            web_jobs.append(DuplicatedJobWeb(job, self.model_web, job_id, self._modeling_obj))

        return web_jobs


class DuplicatedUserJourneyStepWeb(UserJourneyStepWeb):
    def __init__(self, modeling_obj, model_web, web_id, user_journey):
        super().__init__(modeling_obj, model_web)
        self.id = web_id
        self.user_journeys = [user_journey]


class UserJourneyWeb(ModelingObjectWrapper):
    @property
    def uj_steps(self):
        web_uj_steps = []
        for uj_step in self._modeling_obj.uj_steps:
            if len(uj_step.user_journeys) == 1:
                uj_step_id = uj_step.id
            else:
                uj_step_id = f"{uj_step.id}_{self.id}"
            web_uj_steps.append(DuplicatedUserJourneyStepWeb(uj_step, self.model_web, uj_step_id, self._modeling_obj))

        return web_uj_steps

    @property
    def links_to(self):
        linked_server_ids = set()
        for uj_step in self.uj_steps:
            for job in uj_step.jobs:
                linked_server_ids.add(job.server.id)
        return "|".join(sorted(linked_server_ids))


class UsagePatternWeb(ModelingObjectWrapper):
    @property
    def links_to(self):
        return self.user_journey.id

wrapper_mapping = {
    "Job": JobWeb,
    "UserJourneyStep": UserJourneyStepWeb,
    "UserJourney": UserJourneyWeb,
    "UsagePattern": UsagePatternWeb,
}

def wrap_efootprint_object(modeling_obj, model_web):
    if modeling_obj.class_as_simple_str in wrapper_mapping.keys():
        return wrapper_mapping[modeling_obj.class_as_simple_str](modeling_obj, model_web)

    return ModelingObjectWrapper(modeling_obj, model_web)
