from django.template import Context, loader
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest
from django.shortcuts import render_to_response
from django import forms
import TDG, os
import json

def TDGhome(request):
    DATA_PARENT = '/var/lib/'
    DATA_FOLDER = 'testDataGenerator'
    DATA_PATH = DATA_PARENT + '/' + DATA_FOLDER + '/'
    if request.method == 'POST': # If the form has been submitted...        
        if request.POST.has_key('arguments'):
            # Pass the provided arguments to the test data generator
            args = request.POST.getlist('arguments')            

            # The file arguments will be loaded from and outputted to
            #  the directory /var/lib/testDataGenerator.
            if len(args) == 1:
                type = 'election'
                args[0] = DATA_PATH + args[0]
            elif len(args) == 3:
                type = 'counts'
                args[1] = DATA_PATH + args[1]
                args[2] = DATA_PATH + args[2]
#fix        else:
                # Give an error message . . . . . . . . . . . . . . . . 
            P = TDG.Provide_random_ballots(type, args)                  
        elif request.POST.has_key('delete'):
            for file in request.POST.getlist('delete'):
                os.remove(DATA_PATH + file)
        elif request.POST.has_key('oldName'):
            oldName = request.POST['oldName']
            newName = request.POST['newName']
            os.rename(DATA_PATH + oldName
                ,DATA_PATH + newName)
        elif request.POST.has_key('displayThis'):
            displayMe = request.POST['displayThis']
            stream = open(DATA_PATH + displayMe, 'r')
            lines = stream.readlines()                      
            return HttpResponse(lines)
                            
    # Make the directory /var/lib/testDataGenerator if it does
    #  not exist already, generated files will go there.
    if os.listdir(DATA_PARENT).count(DATA_FOLDER) == 0:
        os.mkdir(DATA_PATH)

    # Get a list of files so far generated  
    files = sorted(os.listdir(DATA_PATH))
    
    c = Context({'filelist': files })   
    return render_to_response("TDGhomeTemplate.html", c)
