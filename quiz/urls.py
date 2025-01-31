from django.urls import path

from . import views

urlpatterns = [
    path("onboarding", views.onboarding, name="onboarding"),
    path("usage-journeys", views.usage_journeys, name="usage-journeys"),
    path("usage-journeys/add-step", views.add_usage_journey_step, name="add_usage_journey_step"),
    path("services", views.services, name="services"),
    path("usage-patterns", views.form_usage_pattern, name="form_usage_pattern"),
    path("analyze", views.analyze, name="analyze"),
    path("import-json", views.import_json, name="import-json")
]
