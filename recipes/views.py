from django.http import HttpResponse
from django.shortcuts import render


def home(request):
    return render(request,'global/home.html')

def contato(request):
    return HttpResponse('CONTATO')

def sobre(request):
    return HttpResponse('SOBRE')