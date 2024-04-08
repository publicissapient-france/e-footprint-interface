from django.urls import path

from . import views

urlpatterns = [
    path("", views.analyze, name="analyze"),
    path("redirect-to-model-builder", views.redirect_to_model_builder, name="redirect_to_model_builder")
]
