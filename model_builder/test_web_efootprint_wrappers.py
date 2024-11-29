from unittest import TestCase

from efootprint.builders.hardware.storage_defaults import default_ssd

from model_builder.web_efootprint_wrappers import ModelingObjectWrapper


class StorageWeb(ModelingObjectWrapper):
    @property
    def id(self):
        return f"{self._modeling_obj.id}_modeling_obj"


class TestWebEfootprintWrappers(TestCase):
    def test_storage_web_id(self):
        storage = default_ssd()
        storage_web = StorageWeb(storage)

        self.assertEqual(f"{storage.id}_modeling_obj", storage_web.id)
