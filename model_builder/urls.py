from django.urls import path

import model_builder.views_addition
import model_builder.views_deletion
import model_builder.views_edition
from . import views

urlpatterns = [
    path("", views.model_builder_main, name="model-builder"),
    path("<reboot>", views.model_builder_main, name="model-builder"),
    path("open-create-object-panel/<object_type>/",
         model_builder.views_addition.open_create_object_panel, name="open-add-new-object-panel-with-object-structure-defined"),
    path("open-create-server-panel/",
         model_builder.views_addition.open_create_server_panel, name="open-create-server-panel"),
    path("open-create-service-panel/<server_efootprint_id>/",
         model_builder.views_addition.open_create_service_panel, name="open-create-service-panel"),
    path("open_create_job_panel/",
         model_builder.views_addition.open_create_job_panel, name="open-create-job-panel"),
    path('open-create-usage-pattern-panel/', model_builder.views_addition.open_create_usage_pattern_panel,
         name='open-create-usage-pattern-panel'),
    path("add-new-user-journey-step/<usage_journey_efootprint_id>/",
         model_builder.views_addition.add_new_usage_journey_step, name="add-new-user-journey-step"),
    path('add-new-user-journey/', model_builder.views_addition.add_new_usage_journey, name='add-new-user-journey'),
    path('add-new-usage-pattern/', model_builder.views_addition.add_new_usage_pattern, name='add-new-usage-pattern'),
    path('add-new-server/', model_builder.views_addition.add_new_server, name='add-new-server'),
    path('add-new-service/<server_efootprint_id>', model_builder.views_addition.add_new_service,
         name='add-add_new_service'),
    path("add-new-job/<usage_journey_step_efootprint_id>/",model_builder.views_addition.add_new_job, name="add-new-job"),
    path("open-edit-object-panel/<object_id>/", model_builder.views_edition.open_edit_object_panel,
         name="open-edit-object-panel"),
    path("edit-object/<object_id>/", model_builder.views_edition.edit_object, name="edit-object"),
    path("delete-object", model_builder.views_deletion.delete_object, name="delete-object"),
    path("download-json", views.download_json, name="download-json"),
]
