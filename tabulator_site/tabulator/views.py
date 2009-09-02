import os
import json

from django.template import Context, loader
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest
from django.shortcuts import render_to_response
from django import forms
from django.conf import settings

import HWT
import TDG
import tabulator

def TDG_home(request):
    # Check to see if the client is submitting data.
    if request.method == 'POST':
        # Check to see if the client wants to generate a file
        if request.POST.has_key('arguments'):            
            # Get and deserialize the users arguemnts from JSON
            args = request.POST.getlist('arguments')
            args = json.loads(args[0])

            # Arguments will be made consistent with where data is
            #  stored on the server, as given by DATA_PATH_TDG
            if len(args) == 1:
                type = 'election'
                args[0] = settings.DATA_PATH_TDG + args[0]
            elif len(args) == 3:
                type = 'counts'
                args[1] = settings.DATA_PATH_TDG + args[1]
                args[2] = settings.DATA_PATH_TDG + args[2]
            P = TDG.ProvideRandomBallots(type, args)  # Make a file
        # Check to see if client wants to delete file(s)
        elif request.POST.has_key('delete'):
            for file in request.POST.getlist('delete'):
                os.remove(settings.DATA_PATH_TDG + file)
        # Check to see if client wants to rename a file
        elif request.POST.has_key('old_name'):
            old_name = request.POST['old_name']
            new_name = request.POST['new_name']
            os.rename(settings.DATA_PATH_TDG + old_name
                ,settings.DATA_PATH_TDG + new_name)
        # Check to see if client wants the contents of a generated file
        elif request.POST.has_key('display_this'):
            display_me = request.POST['display_this']
            stream = open(settings.DATA_PATH_TDG + display_me, 'r')
            lines = stream.readlines()
            return HttpResponse(lines)
                            
    # Make the subdirectory specified by DATA_FOLDER_TDG within the
    #  directory DATA_PARENT, if it does not exist already. Generated
    #  test data files will go here.
    if os.listdir(settings.DATA_PARENT).count(settings.DATA_FOLDER_TDG) == 0:
        os.mkdir(settings.DATA_PATH_TDG)

    # Get a list of files so far generated  
    files = sorted(os.listdir(settings.DATA_PATH_TDG))
    
    c = Context({'filelist': files })   
    return render_to_response("tdg_template.html", c)

def tabulator_home(request):
    if request.method == 'POST':  # If the form has been submitted...
        if request.POST.has_key('hello_world'):                        
            h = HWT.HWTabulator(' ', ' ', ' ', settings.DATA_PATH_TAB + 'hello_world')
            stream = open(settings.DATA_PATH_TAB + 'hello_world', 'r')
            lines = stream.readlines()                    
            return HttpResponse(lines)    
    if os.listdir(settings.DATA_PARENT).count(settings.DATA_FOLDER_TAB) == 0:
        os.mkdir(settings.DATA_PATH_TAB)
    return render_to_response("tabulator_template.html")
