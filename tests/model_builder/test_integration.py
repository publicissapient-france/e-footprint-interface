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
        system_data_path = os.path.join("model_builder", "default_system_data.json")

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
            'form_add_devices': [list(DEFAULT_HARDWARES.keys())[0]],
            'form_add_network': [list(DEFAULT_NETWORKS.keys())[0]],
            'form_add_country': [list(DEFAULT_COUNTRIES.keys())[0]],
            'form_add_usage_journey': ['uuid-Daily-video-usage'],
            'form_add_date_hourly_usage_journey_starts': ['2025-02-01'],
            'form_add_list_hourly_usage_journey_starts': ['6,6,6,6,6,6,69,9,9,9,9,9,10,10,10,10,10,10,10,10,10'],
            'form_add_name': ['2New usage pattern'],
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
        post_data.update({'form_add_name': ['New service'],
                          'form_add_type_object_available': ['WebApplication'],
                          'form_add_technology': ['php-symfony'], 'form_add_base_ram_consumption': ['2'],
                          'form_add_bits_per_pixel': ['0.1'], 'form_add_static_delivery_cpu_cost': ['4.0'],
                          'form_add_ram_buffer_per_user': ['50']}
        )

        service_request = self.factory.post('/add_new_service/uuid-Server-1', data=post_data)
        self._add_session_to_request(service_request, up_request.session["system_data"])
        response = add_new_service(service_request, 'uuid-Server-1')
        service_id = next(iter(service_request.session["system_data"]["WebApplication"].keys()))
        self.assertEqual(response.status_code, 200)

        logger.info(f"Creating job")
        post_data = QueryDict(mutable=True)
        post_data.update(
        {'form_add_name': ['New job'], 'form_add_server': ['uuid-Server-1'],
         'form_add_service': [service_id],
         'form_add_type_object_available': ['WebApplicationJob'],
         'form_add_implementation_details': ['aggregation-code-side'],
         'form_add_data_transferred': ['150'], 'form_add_data_stored': ['100']}
        )

        job_request = self.factory.post('/model_builder/add-new-job/uuid-20-min-streaming-on-Youtube/', data=post_data)
        self._add_session_to_request(job_request, service_request.session["system_data"])
        response = add_new_job(job_request, "uuid-20-min-streaming-on-Youtube")
        self.assertEqual(response.status_code, 200)
        new_job_id = next(iter(job_request.session["system_data"]["WebApplicationJob"].keys()))

        logger.info(f"Deleting usage pattern")
        delete_object(job_request, new_up_id)
        logger.info(f"Deleting job")
        delete_object(job_request, new_job_id)
        logger.info(f"Deleting service")
        delete_object(job_request, service_id)

        self.assertEqual(job_request.session["system_data"], self.system_data)
