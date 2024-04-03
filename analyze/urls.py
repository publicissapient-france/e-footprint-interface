from django.urls import path

from . import views

urlpatterns = [
    path("", views.analyze, name="analyze"),
    path("response", views.response, name="response"),
    path("update-value", views.update_value, name="update_value"),
]
