from django.urls import path

from . import views

urlpatterns = [
    path("", views.model_builder_main, name="model-builder"),
    path("open-add-new-object-panel", views.open_add_new_object_panel, name="open-add-new-object-panel"),
    path("add-new-object", views.add_new_object, name="add-new-object"),
    path("open-edit-object-panel", views.open_edit_object_panel, name="open-edit-object-panel"),
    path("close-form", views.close_form, name="close-form"),
    path("update-value", views.update_value, name="update_value"),
]
