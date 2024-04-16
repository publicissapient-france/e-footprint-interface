from django.urls import path

from . import views

urlpatterns = [
    path("", views.model_builder_main, name="model-builder"),
    path("open-object-panel", views.open_object_panel, name="open-add-new-object-panel"),
    path("add-new-object", views.add_new_object, name="add-new-object"),
    path("close-form", views.close_form, name="close-form"),
    path("update-value", views.update_value, name="update_value"),
    path("delete-object", views.delete_object, name="delete-object")
]
