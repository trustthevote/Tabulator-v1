import os
import json

from django.template import Context, loader
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest
from django.shortcuts import render_to_response
from django.conf import settings

import HWT
import TDG
import tabulator
import audit_header

def tabulator_home(request):
    # Check to see if the client is submitting data.
    if request.method == 'POST':
        # Check to see if the client wants to generate a file
        if request.POST.has_key('arguments_tdg'):            
            # Get and deserialize the users arguments from JSON
            args = request.POST.getlist('arguments_tdg')
            args = json.loads(args[0])

            # Arguments will be made consistent with where data is
            #  stored on the server, as given by DATA_PATH
            if len(args) == 1:
                type = 'election'
                args[0] = settings.DATA_PATH + 'prec_cont/' + args[0]
            elif len(args) == 3:
                type = 'counts'
                args[1] = settings.DATA_PATH + 'prec_cont/' + args[1]
                args[2] = settings.DATA_PATH + 'bal_count_tot/' + args[2]
            P = TDG.ProvideRandomBallots(type, args)  # Make a file            
            return HttpResponse()
        # Check to see if client wants to merge files
        if request.POST.has_key('arguments'):
            # Get and deserialize the users arguments from JSON
            args = request.POST.getlist('arguments')
            args = json.loads(args[0])
            # Arguments will be made consistent with where data is
            #  stored on the server, as given by DATA_PATH
            args[0] = settings.DATA_PATH + 'prec_cont/' + args[0]
            args[1] = settings.DATA_PATH + 'bal_count_tot/' + args[1]
            args[2] = settings.DATA_PATH + 'bal_count_tot/' + args[2]
            fname = args[3]
            args[3] = settings.DATA_PATH + 'tab_aggr/' + args[3]
            args.append(settings.DATA_PATH + 'reports/' + fname + '_report')            

            P = tabulator.Tabulator(args[0], args[1], args[2], args[3], args[4])
            return HttpResponse()
        # Check to see if client wants to delete file(s)
        elif request.POST.has_key('delete'):
            for file in request.POST.getlist('delete'):
                if os.listdir(settings.DATA_PATH + 'prec_cont/').count(file) == 1:
                    os.remove(settings.DATA_PATH + 'prec_cont/' + file)
                elif os.listdir(settings.DATA_PATH + 'bal_count_tot/').count(file) == 1:
                    os.remove(settings.DATA_PATH + 'bal_count_tot/' + file)                
                else:
                    os.remove(settings.DATA_PATH + 'tab_aggr/' + file)
                    os.remove(settings.DATA_PATH + 'reports/' + file + "_report")
        # Check to see if client wants to rename a file
        elif request.POST.has_key('old_name'):
            old_name = request.POST['old_name']
            new_name = request.POST['new_name']
            if os.listdir(settings.DATA_PATH + 'prec_cont/').count(old_name) == 1:
                os.rename(settings.DATA_PATH + 'prec_cont/' + old_name,
                    settings.DATA_PATH + 'prec_cont/' + new_name)
            elif os.listdir(settings.DATA_PATH + 'bal_count_tot/').count(old_name) == 1:
                os.rename(settings.DATA_PATH + 'bal_count_tot/' + old_name,
                    settings.DATA_PATH + 'bal_count_tot/' + new_name)
            else:
                os.rename(settings.DATA_PATH + 'tab_aggr/' + old_name,
                    settings.DATA_PATH + 'tab_aggr/' + new_name)
                os.rename(settings.DATA_PATH + 'reports/' + old_name + '_report',
                    settings.DATA_PATH + 'reports/' + new_name + '_report')
        # Check to see if client wants the contents of a tdg file
        elif request.POST.has_key('display_this_tdg'):
            file = request.POST['display_this_tdg']
            if os.listdir(settings.DATA_PATH + 'prec_cont/').count(file) == 1:
                stream = open(settings.DATA_PATH + 'prec_cont/' + file, 'r')                    
            else:
                stream = open(settings.DATA_PATH + 'bal_count_tot/' + file, 'r')
            lines = stream.readlines()
            return HttpResponse(lines)
        # Check to see if client wants the contents of tabulator files
        elif request.POST.has_key('display_this'):
            fname = request.POST['display_this']
            lines = {}
            stream = open(settings.DATA_PATH + 'tab_aggr/' + fname, 'r')
            lines["merge"] = stream.readlines()
            stream = open(settings.DATA_PATH + 'reports/' + fname + '_report', 'r')
            lines["report"] = stream.readlines()
            lines_json = json.dumps(lines)
            return HttpResponse(lines_json)
        elif request.POST.has_key('welcome_tab'):
            c = get_render_data()
            return render_to_response('welcome_template.html', c)
        elif request.POST.has_key('tdg_tab'):            
            c = get_render_data()
            return render_to_response('tdg_template.html', c)
        elif request.POST.has_key('tabulator_tab'):
            c = get_render_data()
            return render_to_response('tabulator_template.html', c)
    c = get_render_data()
    return render_to_response('welcome_template.html', c)

def get_render_data():
    # Make the subdirectory specified by DATA_PATH within the
    #  directory DATA_PARENT, if it does not exist already. Generated
    #  test data files will go here.    
    if os.listdir(settings.DATA_PARENT).count(settings.DATA_FOLDER) == 0:
        os.mkdir(settings.DATA_PATH)
    if os.listdir(settings.DATA_PATH).count('prec_cont') == 0:
        os.mkdir(settings.DATA_PATH + 'prec_cont/')
    if os.listdir(settings.DATA_PATH).count('bal_count_tot') == 0:
        os.mkdir(settings.DATA_PATH + 'bal_count_tot/')
    if os.listdir(settings.DATA_PATH).count('tab_aggr') == 0:
        os.mkdir(settings.DATA_PATH + 'tab_aggr/')
    if os.listdir(settings.DATA_PATH).count('reports') == 0:
        os.mkdir(settings.DATA_PATH + 'reports/')

    # Get a list of files so far generated, by type and combined
    prec_files = os.listdir(settings.DATA_PATH + 'prec_cont/')
    bal_files = os.listdir(settings.DATA_PATH + 'bal_count_tot/')
    tdg_files = sorted(prec_files + bal_files)
    tab_files = os.listdir(settings.DATA_PATH + 'tab_aggr/')
    reports = os.listdir(settings.DATA_PATH + 'reports/')


    # Get version / last revision info from file
    stream = open('VERSION', 'r')
    version = stream.readlines()

    return Context({'prec_files':prec_files, 'bal_files':bal_files,
                  'tdg_files':tdg_files, 'tab_files':tab_files,
                  'reports':reports, 'version':version})
