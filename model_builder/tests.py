import os
import json

from django.contrib.sessions.middleware import SessionMiddleware
from django.test import TestCase, RequestFactory
from django.http import QueryDict
from unittest.mock import patch
from model_builder.views_addition import add_new_usage_pattern
from model_builder.model_web import ModelWeb, DEFAULT_HARDWARES, DEFAULT_NETWORKS, DEFAULT_COUNTRIES


class AddNewUsagePatternTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        system_data_path = os.path.join("model_builder", "default_system_data.json")

        # Load system data
        with open(system_data_path, "r") as f:
            self.system_data = json.load(f)

        # Mock POST data
        self.post_data = QueryDict(mutable=True)
        self.post_data.update({
            'csrfmiddlewaretoken': ['ruwwTrYareoTugkh9MF7b5lhY3DF70xEwgHKAE6gHAYDvYZFDyr1YiXsV5VDJHKv'],
            'form_add_devices': [list(DEFAULT_HARDWARES.keys())[0]],
            'form_add_network': [list(DEFAULT_NETWORKS.keys())[0]],
            'form_add_country': [list(DEFAULT_COUNTRIES.keys())[0]],
            'form_add_usage_journey': ['uuid-Daily-video-usage'],
            'form_add_date_hourly_usage_journey_starts': ['2025-02-01'],
            'form_add_list_hourly_usage_journey_starts': ['6,6,6,6,6,6,69,9,9,9,9,9,10,10,10,10,10,10,10,10,10'],
            'form_add_name': ['2New usage pattern'],
        })

    def _add_session_to_request(self, request):
        """Attach a session to the request object using Django's session middleware."""
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session["system_data"] = self.system_data
        request.session.save()

    def test_add_new_usage_pattern(self):
        """Test that add_new_usage_pattern processes the request correctly and returns the expected response."""
        request = self.factory.post('/add_new_usage_pattern/', data=self.post_data)
        self._add_session_to_request(request)  # Attach a valid session

        response = add_new_usage_pattern(request)

        self.assertEqual(response.status_code, 200)
