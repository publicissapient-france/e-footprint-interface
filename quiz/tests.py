from django.test import TestCase
from django.urls import reverse
from django.test import Client


class HelloWorldTestCase(TestCase):
    def test_book_infos_view(self):
        client = Client()
        path = reverse("onboarding")
        response = client.get(path)
        assert response.status_code == 200
