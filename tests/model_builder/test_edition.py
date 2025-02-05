import os
import json

from django.contrib.sessions.middleware import SessionMiddleware
from django.test import TestCase, RequestFactory
from django.http import QueryDict
from efootprint.logger import logger

from model_builder.class_structure import generate_object_edition_structure
from model_builder.views_addition import add_new_usage_pattern, add_new_service, add_new_job
from model_builder.model_web import DEFAULT_HARDWARES, DEFAULT_NETWORKS, DEFAULT_COUNTRIES, ModelWeb
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

    def test_edition(self):
        logger.info(f"Creating service")
        post_data = QueryDict(mutable=True)
        post_data.update({'name': ['New service'],
                          'type_object_available': ['WebApplication'],
                          'technology': ['php-symfony'], 'base_ram_consumption': ['2'],
                          'bits_per_pixel': ['0.1'], 'static_delivery_cpu_cost': ['4.0'],
                          'ram_buffer_per_user': ['50']}
        )

        service_request = self.factory.post('/add_new_service/uuid-Server-1', data=post_data)
        self._add_session_to_request(service_request, self.system_data)
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

        model_web = ModelWeb(job_request.session)
        job = model_web.get_web_object_from_efootprint_id(new_job_id)

        job_edition_structure, dynamic_form_data = generate_object_edition_structure(job)

        ref_job_edition_structure = {'fields': [{'id': 'implementation_details',
             'input_type': 'select',
             'name': 'implementation_details',
             'options': [{'label': 'aggregation-code-side',
                          'value': 'aggregation-code-side'},
                         {'label': 'default', 'value': 'default'},
                         {'label': 'mysql', 'value': 'mysql'},
                         {'label': 'no-index', 'value': 'no-index'},
                         {'label': 'no-pagination', 'value': 'no-pagination'},
                         {'label': 'orm-loop', 'value': 'orm-loop'}],
             'selected': "aggregation-code-side"},
            {'default': 150.0,
             'id': 'data_transferred',
             'input_type': 'input',
             'name': 'data_transferred',
             'unit': 'MB'},
            {'default': 100.0,
             'id': 'data_stored',
             'input_type': 'input',
             'name': 'data_stored',
             'unit': 'kB'}],
             'list_attributes': [],
             'modeling_obj_attributes': [
                 {'attr_name': 'service',
                  'attr_value': model_web.get_web_object_from_efootprint_id(service_id),
                  'existing_objects': [model_web.get_web_object_from_efootprint_id(service_id)],
        'object_type': 'WebApplication'}]
        }

        ref_dynamic_form_data = {'dynamic_lists': []}

        self.assertDictEqual(job_edition_structure, ref_job_edition_structure)
        self.assertDictEqual(dynamic_form_data, ref_dynamic_form_data)
