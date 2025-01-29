import json
import os
from unittest import TestCase

from e_footprint_interface import settings
from efootprint.logger import logger
from model_builder.class_structure import efootprint_class_structure


class TestsClassStructure(TestCase):
    @classmethod
    def setUpClass(cls):
        with open(os.path.join(settings.BASE_DIR, 'theme', 'static', 'object_inputs_and_default_values.json'),
                  "r") as object_inputs_file:
            cls.object_inputs_and_default_values = json.load(object_inputs_file)

    def test_structures(self):
        for class_name in self.object_inputs_and_default_values.keys():
            logger.info(f"Testing {class_name} structure")
            ref_struct = self.object_inputs_and_default_values[class_name]
            ref_struct.pop("hourly_quantities_attributes")
            ref_struct.update({"str_attributes": {}, "conditional_str_attributes": {}})
            self.assertDictEqual(ref_struct, efootprint_class_structure(class_name))

    def test_services_structure(self):
        video_streaming_structure = efootprint_class_structure("VideoStreaming")
        genai_structure = efootprint_class_structure("GenAIModel")
        web_app_structure = efootprint_class_structure("WebApplication")
        a = 1
