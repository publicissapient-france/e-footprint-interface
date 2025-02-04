import os
import json

from django.contrib.sessions.middleware import SessionMiddleware
from django.test import TestCase, RequestFactory
from django.http import QueryDict
from model_builder.views_addition import add_new_usage_pattern, add_new_service, add_new_job
from model_builder.model_web import DEFAULT_HARDWARES, DEFAULT_NETWORKS, DEFAULT_COUNTRIES


class AddNewUsagePatternTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        system_data_path = os.path.join("model_builder", "default_system_data.json")

        # Load system data
        with open(system_data_path, "r") as f:
            self.system_data = json.load(f)

    def _add_session_to_request(self, request):
        """Attach a session to the request object using Django's session middleware."""
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session["system_data"] = self.system_data
        request.session.save()

    def test_add_new_usage_pattern(self):
        """Test that add_new_usage_pattern processes the request correctly and returns the expected response."""
        post_data = QueryDict(mutable=True)
        post_data.update({
            'csrfmiddlewaretoken': ['ruwwTrYareoTugkh9MF7b5lhY3DF70xEwgHKAE6gHAYDvYZFDyr1YiXsV5VDJHKv'],
            'devices': [list(DEFAULT_HARDWARES.keys())[0]],
            'network': [list(DEFAULT_NETWORKS.keys())[0]],
            'country': [list(DEFAULT_COUNTRIES.keys())[0]],
            'usage_journey': ['uuid-Daily-video-usage'],
            'date_hourly_usage_journey_starts': ['2025-02-01'],
            'list_hourly_usage_journey_starts': ['6,6,6,6,6,6,69,9,9,9,9,9,10,10,10,10,10,10,10,10,10'],
            'name': ['2New usage pattern'],
        })

        request = self.factory.post('/add_new_usage_pattern/', data=post_data)
        self._add_session_to_request(request)  # Attach a valid session
        len_system_up = len(request.session["system_data"]["System"]["uuid-system-1"]["usage_patterns"])

        response = add_new_usage_pattern(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(request.session["system_data"]["UsagePattern"]), len_system_up + 1)

    def test_add_web_service_then_web_job(self):
        post_data = QueryDict(mutable=True)
        post_data.update({'name': ['New service'],
                          'type_object_available': ['WebApplication'],
                          'technology': ['php-symfony'], 'base_ram_consumption': ['2'],
                          'bits_per_pixel': ['0.1'], 'static_delivery_cpu_cost': ['4.0'],
                          'ram_buffer_per_user': ['50']}
        )

        request = self.factory.post('/add_new_service/uuid-Server-1', data=post_data)
        self._add_session_to_request(request)

        response = add_new_service(request, 'uuid-Server-1')
        service_id = next(iter(request.session["system_data"]["WebApplication"].keys()))
        self.assertEqual(response.status_code, 200)

        post_data = QueryDict(mutable=True)
        post_data.update(
        {'name': ['New job'], 'server': ['uuid-Server-1'],
         'service': [service_id],
         'type_object_available': ['WebApplicationJob'],
         'implementation_details': ['aggregation-code-side'],
         'data_transferred': ['2.2', '150'], 'data_stored': ['100', '100'],
         'request_duration': ['1'], 'compute_needed': ['0.1'],
         'ram_needed': ['50']}
        )

        request = self.factory.post('/model_builder/add-new-job/uuid-20-min-streaming-on-Youtube/', data=post_data)
        self._add_session_to_request(request)

        response = add_new_job(request, "uuid-20-min-streaming-on-Youtube")
        self.assertEqual(response.status_code, 200)
