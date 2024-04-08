from utils import htmx_render
from model_builder.views import model_builder_main

from django.shortcuts import render


def analyze(request):
    return htmx_render(request, "analyze/analyze.html")


def redirect_to_model_builder(request):
    return model_builder_main(request)


def load_graph_script(request):
    return render(request, "analyze/graph-drawing-script.html")
