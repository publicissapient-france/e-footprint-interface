from django.shortcuts import render


def home(request):
    return render(request, "home.html")


def understand(request):
    return render(request, "understand.html")
