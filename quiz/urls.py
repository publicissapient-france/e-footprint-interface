from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("quiz/understand", views.understand, name="understand"),
    path("quiz/analyze/onboarding", views.analyze_onboarding, name="analyze-onboarding"),
    path("quiz/analyze/user-journeys", views.analyze_user_journeys, name="user-journeys"),
    path("quiz/analyze/user-journeys/add-step", views.add_user_journey_step, name="user-journeys-add-step"),
    path("quiz/analyze/apis", views.analyze_apis, name="apis"),
    path("quiz/analyze/usage-patterns", views.analyze_usage_patterns, name="usage-patterns"),
    path("quiz/analyze/", views.analyze, name="analyze"),
    path("quiz/analyze/response", views.response, name="response"),
    path("quiz/analyze/update-value", views.update_value, name="update_value"),
    path("quiz/form", views.form, name="form"),
    path("quiz/form-service", views.form_service, name="form_service"),
    path("quiz/form-usage-pattern", views.form_usage_pattern, name="form_usage_pattern"),
]
