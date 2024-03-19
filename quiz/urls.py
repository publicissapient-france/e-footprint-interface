from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("form", views.index, name="index"),
    path("response", views.response, name="response")
]
