import os
import json

from django.contrib.sessions.middleware import SessionMiddleware
from django.test import TestCase, RequestFactory

class TestModelingBase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        system_data_path = os.path.join("tests", "model_builder", "default_system_data.json")

        # Load system data
        with open(system_data_path, "r") as f:
            self.system_data = json.load(f)

    @staticmethod
    def _add_session_to_request(request, system_data):
        """Attach a session to the request object using Django's session middleware."""
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session["system_data"] = system_data
        request.session.save()
