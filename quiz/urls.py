from django.urls import path

from . import views

urlpatterns = [
    path("onboarding", views.onboarding, name="onboarding"),
    path("user-journeys", views.user_journeys, name="user-journeys"),
    path("user-journeys/add-step", views.add_user_journey_step, name="add_user_journey_step"),
    path("apis", views.apis, name="apis"),
    path("usage-patterns", views.usage_patterns, name="usage-patterns"),
    path("form", views.form, name="form"),
    path("services", views.services, name="services"),
    path("form-usage-pattern", views.form_usage_pattern, name="form_usage_pattern"),
]
