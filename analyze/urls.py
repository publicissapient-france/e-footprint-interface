from django.urls import path

from . import views

urlpatterns = [
    path("", views.analyze, name="analyze"),
    path("response", views.response, name="response"),
    path("add-service", views.add_service, name="add-service"),
    path("update-value", views.update_value, name="update_value"),
]
