from django.urls import path

from . import views

urlpatterns = [
    path("", views.model_builder_main, name="model-builder"),
    path("open-create-object-panel/<object_type>/", views.open_create_object_panel, name="open-add-new-object-panel"),
    path("open-edit-object-panel/<object_type>/", views.open_edit_object_panel, name="open-edit-object-panel"),
    path("add-new-object", views.add_new_object, name="add-new-object"),
    path("edit-object", views.edit_object, name="edit-object"),
    path("delete-object", views.delete_object, name="delete-object"),
    path("download-json", views.download_json, name="download-json"),
    path("set-reference-model", views.set_as_reference_model, name="set-reference-model"),
    path("compare_with_reference", views.compare_with_reference, name="compare_with_reference"),
    path("reset_model_reference", views.reset_model_reference, name="reset_model_reference")
]
