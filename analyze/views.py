from utils import htmx_render
from model_builder.views import model_builder_main


def analyze(request):
    return htmx_render(request, "analyze.html")


def redirect_to_model_builder(request):
    return model_builder_main(request)
