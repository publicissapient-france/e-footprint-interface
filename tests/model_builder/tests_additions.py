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
            'form_add_devices': [list(DEFAULT_HARDWARES.keys())[0]],
            'form_add_network': [list(DEFAULT_NETWORKS.keys())[0]],
            'form_add_country': [list(DEFAULT_COUNTRIES.keys())[0]],
            'form_add_usage_journey': ['uuid-Daily-video-usage'],
            'form_add_date_hourly_usage_journey_starts': ['2025-02-01'],
            'form_add_list_hourly_usage_journey_starts': ['6,6,6,6,6,6,69,9,9,9,9,9,10,10,10,10,10,10,10,10,10'],
            'form_add_name': ['2New usage pattern'],
        })

        request = self.factory.post('/add_new_usage_pattern/', data=post_data)
        self._add_session_to_request(request)  # Attach a valid session

        response = add_new_usage_pattern(request)

        self.assertEqual(response.status_code, 200)

    def test_add_web_service_then_web_job(self):
        post_data = QueryDict(mutable=True)
        post_data.update({'form_add_name': ['New service'],
                          'form_add_type_object_available': ['WebApplication'],
                          'form_add_technology': ['php-symfony'], 'form_add_base_ram_consumption': ['2'],
                          'form_add_bits_per_pixel': ['0.1'], 'form_add_static_delivery_cpu_cost': ['4.0'],
                          'form_add_ram_buffer_per_user': ['50']}
        )

        request = self.factory.post('/add_new_service/uuid-Server-1', data=post_data)
        self._add_session_to_request(request)

        response = add_new_service(request, 'uuid-Server-1')
        service_id = next(iter(request.session["system_data"]["WebApplication"].keys()))
        self.assertEqual(response.status_code, 200)

        post_data = QueryDict(mutable=True)
        post_data.update(
        {'form_add_name': ['New job'], 'form_add_server': ['uuid-Server-1'],
         'form_add_service': [service_id],
         'form_add_type_object_available': ['WebApplicationJob'],
         'form_add_implementation_details': ['aggregation-code-side'],
         'form_add_data_transferred': ['2.2', '150'], 'form_add_data_stored': ['100', '100'],
         'form_add_request_duration': ['1'], 'form_add_compute_needed': ['0.1'],
         'form_add_ram_needed': ['50']}
        )

        request = self.factory.post('/model_builder/add-new-job/uuid-20-min-streaming-on-Youtube/', data=post_data)
        self._add_session_to_request(request)

        response = add_new_job(request, "uuid-20-min-streaming-on-Youtube")
        self.assertEqual(response.status_code, 200)
