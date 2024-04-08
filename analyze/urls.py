from django.urls import path

from . import views

urlpatterns = [
    path("", views.analyze, name="analyze"),
    path("redirect-to-model-builder", views.redirect_to_model_builder, name="redirect_to_model_builder"),
    path("load-graph-script", views.load_graph_script, name="load_graph_script")
]
