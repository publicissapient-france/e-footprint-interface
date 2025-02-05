import os
import json

from django.contrib.sessions.middleware import SessionMiddleware
from django.test import TestCase, RequestFactory
from django.http import QueryDict
from efootprint.logger import logger

from model_builder.views_addition import add_new_usage_pattern, add_new_service, add_new_job
from model_builder.model_web import DEFAULT_HARDWARES, DEFAULT_NETWORKS, DEFAULT_COUNTRIES
from model_builder.views_deletion import delete_object


class AddNewUsagePatternTestCase(TestCase):
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

    def test_integration(self):
        logger.info(f"Creating usage pattern")
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

        up_request = self.factory.post('/add_new_usage_pattern/', data=post_data)
        self._add_session_to_request(up_request, self.system_data)  # Attach a valid session
        len_system_up = len(up_request.session["system_data"]["System"]["uuid-system-1"]["usage_patterns"])
        new_up_id = up_request.session["system_data"]["System"]["uuid-system-1"]["usage_patterns"][-1]

        response = add_new_usage_pattern(up_request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(up_request.session["system_data"]["UsagePattern"]), len_system_up + 1)

        logger.info(f"Creating service")
        post_data = QueryDict(mutable=True)
        post_data.update({'name': ['New service'],
                          'type_object_available': ['WebApplication'],
                          'technology': ['php-symfony'], 'base_ram_consumption': ['2'],
                          'bits_per_pixel': ['0.1'], 'static_delivery_cpu_cost': ['4.0'],
                          'ram_buffer_per_user': ['50']}
        )

        service_request = self.factory.post('/add_new_service/uuid-Server-1', data=post_data)
        self._add_session_to_request(service_request, up_request.session["system_data"])
        response = add_new_service(service_request, 'uuid-Server-1')
        service_id = next(iter(service_request.session["system_data"]["WebApplication"].keys()))
        self.assertEqual(response.status_code, 200)

        logger.info(f"Creating job")
        post_data = QueryDict(mutable=True)
        post_data.update(
        {'name': ['New job'], 'server': ['uuid-Server-1'],
         'service': [service_id],
         'type_object_available': ['WebApplicationJob'],
         'implementation_details': ['aggregation-code-side'],
         'data_transferred': ['150'], 'data_stored': ['100']}
        )

        job_request = self.factory.post('/model_builder/add-new-job/uuid-20-min-streaming-on-Youtube/', data=post_data)
        self._add_session_to_request(job_request, service_request.session["system_data"])
        response = add_new_job(job_request, "uuid-20-min-streaming-on-Youtube")
        self.assertEqual(response.status_code, 200)
        new_job_id = next(iter(job_request.session["system_data"]["WebApplicationJob"].keys()))

        logger.info(f"Manually deleting usage pattern")
        delete_object(job_request, new_up_id)
        logger.info(f"Manually deleting job")
        delete_object(job_request, new_job_id)
        logger.info(f"Manually deleting service")
        delete_object(job_request, service_id)

        self.assertEqual(job_request.session["system_data"], self.system_data)
