from django.urls import path

import model_builder.views_addition
import model_builder.views_deletion
import model_builder.views_edition
from . import views

urlpatterns = [
    path("", views.model_builder_main, name="model-builder"),
    path("open-create-object-panel/<object_type>/",
         model_builder.views_addition.open_create_object_panel, name="open-add-new-object-panel-with-object-structure-defined"),
    path("open-create-server-panel/<object_type>/",
         model_builder.views_addition.open_create_server_panel, name="open-create-server-panel"),
    path("add-new-user-journey-step/<user_journey_efootprint_id>/",
         model_builder.views_addition.add_new_user_journey_step, name="add-new-user-journey-step"),
    path('add-new-user-journey/', model_builder.views_addition.add_new_user_journey, name='add-new-user-journey'),
    path('add-new-server/', model_builder.views_addition.add_new_server, name='add-new-server'),
    path("open-edit-object-panel/<object_id>/", model_builder.views_edition.open_edit_object_panel, name="open-edit-object-panel"),
    path("edit-object/<object_id>/", model_builder.views_edition.edit_object, name="edit-object"),
    path("delete-object", model_builder.views_deletion.delete_object, name="delete-object"),
    path("download-json", views.download_json, name="download-json"),
]
