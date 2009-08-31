from django.template import Context, loader
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest
from django.shortcuts import render_to_response
from django import forms
import HWT, os

def tabulatorHome(request):
    DATA_PARENT = '/var/lib/'
    DATA_FOLDER = 'tabulator'
    DATA_PATH = DATA_PARENT + '/' + DATA_FOLDER + '/'
    if request.method == 'POST': # If the form has been submitted...
        if request.POST.has_key('HelloWorld'):            
            print DATA_PATH
            h = HWT.HWTabulator(' ', ' ', ' ', DATA_PATH + 'helloWorld')
            stream = open(DATA_PATH + 'helloWorld', 'r')
            lines = stream.readlines()                    
            return HttpResponse(lines)    
    if os.listdir(DATA_PARENT).count(DATA_FOLDER) == 0:
        os.mkdir(DATA_PATH)
    return render_to_response("TabulatorHomeTemplate.html")
