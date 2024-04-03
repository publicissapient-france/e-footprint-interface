from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("understand", views.understand, name="understand"),
    path("onboarding", views.onboarding, name="analyze-onboarding"),
    path("user-journeys", views.user_journeys, name="user-journeys"),
    path("user-journeys/add-step", views.add_user_journey_step, name="user-journeys-add-step"),
    path("apis", views.apis, name="apis"),
    path("usage-patterns", views.usage_patterns, name="usage-patterns"),
    path("form", views.form, name="form"),
    path("form-service", views.form_service, name="form_service"),
    path("form-usage-pattern", views.form_usage_pattern, name="form_usage_pattern"),
    path("add-step", views.add_step, name="add_step"),
]
