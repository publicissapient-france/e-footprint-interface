from django.urls import path

from . import views

urlpatterns = [
    path("", views.model_builder_main, name="model-builder"),
    path("add-service", views.add_service, name="add-service"),
    path("update-value", views.update_value, name="update_value"),
]
