from django.template import Context, loader
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest
from django.shortcuts import render_to_response
from django import forms
import TDG, os
import json

def TDGhome(request):
    #Set up constants that indicate where on the server test data will
    # be stored.
    DATA_PARENT = '/var/lib/'
    DATA_FOLDER = 'testDataGenerator'
    DATA_PATH = DATA_PARENT + '/' + DATA_FOLDER + '/'
    
    #Check to see if the client is submitting data.
    if request.method == 'POST':
        #Check to see if the client wants to generate a file
        if request.POST.has_key('arguments'):            
            #Get and deserialize the users arguemnts from JSON
            args = request.POST.getlist('arguments')
            args = json.loads(args[0])

            #Arguments will be made consistent with where data is stored
            # on the server, as given by DATA_PATH
            if len(args) == 1:
                type = 'election'
                args[0] = DATA_PATH + args[0]
            elif len(args) == 3:
                type = 'counts'
                args[1] = DATA_PATH + args[1]
                args[2] = DATA_PATH + args[2]
            P = TDG.Provide_random_ballots(type, args) #Generate a file
        #Check to see if client wants to delete file(s)
        elif request.POST.has_key('delete'):
            for file in request.POST.getlist('delete'):
                os.remove(DATA_PATH + file)
        #Check to see if client wants to rename a file
        elif request.POST.has_key('oldName'):
            oldName = request.POST['oldName']
            newName = request.POST['newName']
            os.rename(DATA_PATH + oldName
                ,DATA_PATH + newName)
        #Check to see if client wants the contents of a generated file
        elif request.POST.has_key('displayThis'):
            displayMe = request.POST['displayThis']
            stream = open(DATA_PATH + displayMe, 'r')
            lines = stream.readlines()
            return HttpResponse(lines)
                            
    # Make the subdirectory specified by DATA_FOLDER within the
    #  directory DATA_PARENT, if it does not exist already. Generated
    #  test data files will go here.
    if os.listdir(DATA_PARENT).count(DATA_FOLDER) == 0:
        os.mkdir(DATA_PATH)

    # Get a list of files so far generated  
    files = sorted(os.listdir(DATA_PATH))
    
    c = Context({'filelist': files })   
    return render_to_response("TDGhomeTemplate.html", c)
