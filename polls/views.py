from django.http import HttpResponse


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

def test1(request):
    return HttpResponse("Second Page test")