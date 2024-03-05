from django.http import HttpResponse
from django.shortcuts import render


def index(request):
    return render(request, "quiz/quiz.html")

def response(request):
    return render(request, "quiz/response.html", context={"response": request.POST['json']})