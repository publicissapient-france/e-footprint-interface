from efootprint.abstract_modeling_classes.modeling_object import ModelingObject

class ModelingObjectWrapper:
    def __init__(self, modeling_obj):
        self._modeling_obj = modeling_obj

    def __getattr__(self, name):
        attr = getattr(self._modeling_obj, name)

        if isinstance(attr, list) and len(attr) > 0 and isinstance(attr[0], ModelingObject):
            return [wrap_efootprint_object(item) for item in attr]

        if isinstance(attr, ModelingObject):
            return self.__class__(attr)

        return attr


class JobWeb(ModelingObjectWrapper):
    def __init__(self, modeling_obj, web_id, uj_step):
        super().__init__(modeling_obj)
        self.id = web_id
        self.uj_step = uj_step

    @property
    def appears_in_several_uj_steps(self):
        return len(self._modeling_obj.user_journey_steps) > 1


class UserJourneyStepWeb(ModelingObjectWrapper):
    def __init__(self, modeling_obj, web_id, user_journey):
        super().__init__(modeling_obj)
        self.id = web_id
        self.user_journey = user_journey

    @property
    def jobs(self):
        web_jobs = []
        for job in self._modeling_obj.jobs:
            if len(job.user_journeys) > 1:
                job_id = job.id
            else:
                job_id = f"{job.id}_{self.id}"
            web_jobs.append(JobWeb(job, job_id, self))

        return web_jobs


class UserJourneyWeb(ModelingObjectWrapper):
    @property
    def uj_steps(self):
        web_uj_steps = []
        for uj_step in self._modeling_obj.uj_steps:
            if len(uj_step.user_journeys) > 1:
                uj_step_id = uj_step.id
            else:
                uj_step_id = f"{uj_step.id}_{self.id}"
            web_uj_steps.append(UserJourneyStepWeb(uj_step, uj_step_id, self))

        return web_uj_steps


wrapper_mapping = {
    # TODO: WIP, needs debugging
    # "Job": JobWeb,
    # "UserJourneyStep": UserJourneyStepWeb,
    # "UserJourney": UserJourneyWeb
}

def wrap_efootprint_object(modeling_obj):
    if modeling_obj.class_as_simple_str in wrapper_mapping.keys():
        return wrapper_mapping[modeling_obj.class_as_simple_str](modeling_obj)

    return ModelingObjectWrapper(modeling_obj)
