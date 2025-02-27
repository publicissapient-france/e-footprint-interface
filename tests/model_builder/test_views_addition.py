import os
import json

from efootprint.logger import logger

from django.contrib.sessions.middleware import SessionMiddleware
from django.test import TestCase, RequestFactory
from django.http import QueryDict

from model_builder.views import model_builder_main
from model_builder.views_addition import add_new_usage_pattern, add_new_service, add_new_job
from model_builder.model_web import default_networks, default_devices, default_countries
from model_builder.views_deletion import delete_object
from model_builder.views_edition import edit_object, open_edit_object_panel


class TestViewsAddition(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        system_data_path = os.path.join("tests", "model_builder", "default_system_data.json")

        # Load system data
        with open(system_data_path, "r") as f:
            self.system_data = json.load(f)

    def _add_session_to_request(self, request, system_data):
        """Attach a session to the request object using Django's session middleware."""
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session["system_data"] = system_data
        request.session.save()

    def test_add_new_usage_pattern(self):
        """Test that add_new_usage_pattern processes the request correctly and returns the expected response."""
        post_data = QueryDict(mutable=True)
        post_data.update({
            'csrfmiddlewaretoken': ['ruwwTrYareoTugkh9MF7b5lhY3DF70xEwgHKAE6gHAYDvYZFDyr1YiXsV5VDJHKv'],
            'devices': [list(default_devices().keys())[0]],
            'network': [list(default_networks().keys())[0]],
            'country': [list(default_countries().keys())[0]],
            'usage_journey': ['uuid-Daily-video-usage'],
            'date_hourly_usage_journey_starts': ['2025-02-01'],
            'list_hourly_usage_journey_starts': ['6,6,6,6,6,6,69,9,9,9,9,9,10,10,10,10,10,10,10,10,10'],
            'name': ['2New usage pattern'],
        })

        add_request = self.factory.post('/add_new_usage_pattern/', data=post_data)
        self._add_session_to_request(add_request, self.system_data)  # Attach a valid session
        len_system_up = len(add_request.session["system_data"]["System"]["uuid-system-1"]["usage_patterns"])

        response = add_new_usage_pattern(add_request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(add_request.session["system_data"]["UsagePattern"]), len_system_up + 1)
        up_id = list(add_request.session["system_data"]["UsagePattern"].keys())[-1]

        logger.info("Open edit usage pattern panel")
        open_edit_panel_request = self.factory.get(f'/model_builder/open-edit-object-panel/{up_id}/')
        self._add_session_to_request(open_edit_panel_request, add_request.session["system_data"])
        response = open_edit_object_panel(open_edit_panel_request, up_id)
        self.assertEqual(response.status_code, 200)

        logger.info("Edit usage pattern")
        post_data = QueryDict(mutable=True)
        post_data.update({"name": ['2New usage pattern'],
                          'network': [list(default_networks().keys())[1]],
                          'list_hourly_usage_journey_starts': ['6,6,6,6,6,6,69,9,9,9,9,9,10,10,10,10,10,10,10,10,10'],
                          'date_hourly_usage_journey_starts': ['2025-02-02']})
        edit_request = self.factory.post(f'/model_builder/edit-usage-pattern/{up_id}/', data=post_data)
        self._add_session_to_request(edit_request, add_request.session["system_data"])

        response = edit_object(edit_request, up_id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            add_request.session["system_data"]["UsagePattern"][up_id]["hourly_usage_journey_starts"]["start_date"][:10],
            "2025-02-02")

        logger.info("Reloading page")
        results_request = self.factory.get('/model_builder/')
        self._add_session_to_request(results_request, add_request.session["system_data"])

        response = model_builder_main(results_request)
        self.assertEqual(response.status_code, 200)

        logger.info("Deleting usage pattern")
        delete_request = self.factory.post(f'/model_builder/delete-object/{up_id}/')
        self._add_session_to_request(delete_request, add_request.session["system_data"])

        response = delete_object(delete_request, up_id)

        self.assertEqual(response.status_code, 204)
        self.assertNotIn(up_id, add_request.session["system_data"]["UsagePattern"])
        self.assertEqual(
            len(delete_request.session["system_data"]["System"]["uuid-system-1"]["usage_patterns"]), len_system_up)


    def test_add_web_service_then_web_job(self):
        post_data = QueryDict(mutable=True)
        post_data.update({'name': ['New service'],
                          'type_object_available': ['WebApplication'],
                          'technology': ['php-symfony'], 'base_ram_consumption': ['2'],
                          'bits_per_pixel': ['0.1'], 'static_delivery_cpu_cost': ['4.0'],
                          'ram_buffer_per_user': ['50']}
        )

        request = self.factory.post('/add_new_service/uuid-Server-1', data=post_data)
        self._add_session_to_request(request, self.system_data)

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
        self._add_session_to_request(request, self.system_data)

        response = add_new_job(request, "uuid-20-min-streaming-on-Youtube")
        self.assertEqual(response.status_code, 200)
