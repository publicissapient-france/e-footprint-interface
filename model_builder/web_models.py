from efootprint.api_utils.json_to_system import json_to_system

from model_builder.web_efootprint_wrappers import wrap_efootprint_object


class ModelWeb:
    def __init__(self, jsondata):
        self.jsondata = jsondata
        self.response_objs, self.flat_obj_dict = json_to_system(jsondata)
        self.system = wrap_efootprint_object(list(self.response_objs["System"].values())[0])

        for obj_id, mod_obj in self.flat_obj_dict.items():
            self.flat_obj_dict[obj_id] = wrap_efootprint_object(mod_obj)

        for obj_type in self.response_objs.keys():
            for obj_id, mod_obj in self.response_objs[obj_type].items():
                self.response_objs[obj_type][obj_id] = wrap_efootprint_object(mod_obj)

    def get_objects_from_type(self, obj_type):
        return list(self.response_objs[obj_type].values())

    @property
    def storage(self):
        return self.get_objects_from_type("Storage")

    @property
    def servers(self):
        servers = []

        for server_type in ["Autoscaling", "OnPremise", "Serverless"]:
            if server_type in self.response_objs.keys():
                servers += self.response_objs[server_type].values()

        return servers

    @property
    def autoscaling_servers(self):
        return self.get_objects_from_type("Autoscaling")

    @property
    def on_premise_servers(self):
        return self.get_objects_from_type("OnPremise")

    @property
    def serverless_servers(self):
        return self.get_objects_from_type("Serverless")

    @property
    def jobs(self):
        return self.get_objects_from_type("Job")

    @property
    def uj_steps(self):
        return self.get_objects_from_type("UserJourneyStep")

    @property
    def user_journeys(self):
        return self.get_objects_from_type("UserJourney")

    @property
    def countries(self):
        return self.get_objects_from_type("Country")

    @property
    def hardware(self):
        return self.get_objects_from_type("Hardware")

    @property
    def networks(self):
        return self.get_objects_from_type("Network")

    @property
    def usage_patterns(self):
        return self.get_objects_from_type("UsagePattern")
