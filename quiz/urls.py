from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("quiz/form", views.form, name="form"),
    path("quiz/form-service", views.form_service, name="form_service"),
    path("quiz/form-usage-pattern", views.form_usage_pattern, name="form_usage_pattern"),
    path("quiz/analyze", views.analyze, name="analyze"),
    path("quiz/response", views.response, name="response")
]
