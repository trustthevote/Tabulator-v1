import os
import json

from django.template import Context, loader, RequestContext
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest
from django.shortcuts import render_to_response
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

import HWT
import TDG
import merger
import audit_header


def welcome_handler(request):
    # Check to see if the client is posting data
    if request.method == 'POST':        
        # Check to see if the client is attempting to log in
        if request.POST.has_key('username'):
            logout(request)
            u_attempt = request.POST['username']
            p_attempt = request.POST['password']
            user = authenticate(username=u_attempt, password=p_attempt)
            if user is not None:
                if user.is_active:
                    login(request, user)
            login_status = request.user.is_authenticated()
            return HttpResponse(login_status)            
        # Check to see if the client wants to log the user out
        elif request.POST.has_key('logout_user'):
            logout(request)
    c = get_render_data()
    return render_to_response('welcome.html', c,
     context_instance=RequestContext(request, processors=[settings_processor]))

@login_required
def tdg_handler(request):
    # Check to see if the client is posting data
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
        # Check to see if client wants to delete file(s)
        elif request.POST.has_key('delete'):
            delete_files(request.POST.getlist('delete'))
            return HttpResponse()
        # Check to see if client wants to rename a file
        elif request.POST.has_key('old_name'):
            rename_file(request.POST)
            return HttpResponse()
        # Check to see if the client wants to log the user out
        elif request.POST.has_key('logout_user'):
            logout(request)
            return HttpResponse()
    c = get_render_data()
    return render_to_response('tdg.html', c,
     context_instance=RequestContext(request, processors=[settings_processor]))

@login_required
def tab_handler(request):
    # Check to see if the client is posting data
    if request.method == 'POST':
        # Check to see if client wants to merge files
        if request.POST.has_key('arguments'):
            # Get and deserialize the users arguments from JSON
            args = request.POST.getlist('arguments')
            args = json.loads(args[0])
            # Arguments will be made consistent with where data is
            #  stored on the server, as given by DATA_PATH
            args[0] = settings.DATA_PATH + 'prec_cont/' + args[0]

            if os.listdir(settings.DATA_PATH + 'bal_count_tot/').count(args[1] + '.yaml') == 1:
                args[1] = settings.DATA_PATH + 'bal_count_tot/' + args[1]
            else:
                args[1] = settings.DATA_PATH + 'tab_aggr/' + args[1]
            if os.listdir(settings.DATA_PATH + 'bal_count_tot/').count(args[2] + '.yaml') == 1:
                args[2] = settings.DATA_PATH + 'bal_count_tot/' + args[2]
            else:
                args[2] = settings.DATA_PATH + 'tab_aggr/' + args[2]
            fname = args[3]
            args[3] = settings.DATA_PATH + 'tab_aggr/' + args[3]
            
            m = merger.Merger(args[0], args[1], args[2], args[3])
            if m.validate(args[3] + ".log") == True:
                m.merge(args[3])
            return HttpResponse()
        # Check to see if client wants to delete file(s)
        elif request.POST.has_key('delete'):
            delete_files(request.POST.getlist('delete'))
            return HttpResponse()
        # Check to see if client wants to rename a file
        elif request.POST.has_key('old_name'):
            rename_file(request.POST)
            return HttpResponse()
        # Check to see if the client wants to log the user out
        elif request.POST.has_key('logout_user'):
            logout(request)
            return HttpResponse()
    c = get_render_data()
    return render_to_response('tabulator.html', c,
     context_instance=RequestContext(request, processors=[settings_processor]))

@login_required
def tdg_file_handler(request, fname):
    # Check to see if the client is posting data
    if request.method == 'POST':
        # Check to see if the client wants to log the user out
        if request.POST.has_key('logout_user'):
            logout(request)
            return HttpResponse()
    if os.listdir(settings.DATA_PATH + 'prec_cont/').count(fname) == 1:
        stream = open(settings.DATA_PATH + 'prec_cont/' + fname, 'r')
    else:
        stream = open(settings.DATA_PATH + 'bal_count_tot/' + fname, 'r')
    lines = stream.readlines()
    formatted_lines=[]
    for line in lines:
        line = line.replace('<', '&lt;')
        line = line.replace('>', '&gt;')
        line = line.replace('\t', '   ')
        line = line.replace('\n', '<br/>')        
        formatted_lines.append(line.replace(' ', '&nbsp;'))
    c = get_render_data()
    c['lines'] = formatted_lines
    return render_to_response('tdg_file.html', c,
     context_instance=RequestContext(request, processors=[settings_processor]))

@login_required
def tab_file_handler(request, fname):
    # Check to see if the client is posting data
    if request.method == 'POST':
        # Check to see if the client wants to log the user out
        if request.POST.has_key('logout_user'):
            logout(request)
        return HttpResponse()
    c = get_render_data()
    
    # Read in file data stored on server. A merged file may not have
    #  have been created, but try to load it and format it.
    fname = fname[:fname.rfind('.')]
    stream = open(settings.DATA_PATH + 'tab_aggr/' + fname + '.log', 'r')
    log = stream.readlines()
    formatted_log = []
    for line in log:
        line = line.replace('\n', '<br/>')
        formatted_log.append(line.replace(' ', '&nbsp;'))
    try:
        stream = open(settings.DATA_PATH + 'tab_aggr/' + fname + '.yaml', 'r')
    except IOError:
        pass
    else:
        merged = stream.readlines()
        formatted_merged = []
        for line in merged:
            line = line.replace('<', '&lt;')
            line = line.replace('>', '&gt;')            
            line = line.replace('\t', '   ')
            line = line.replace('\n', '</p>')        
            formatted_merged.append(line.replace(' ', '&nbsp;'))    
        c['merged'] = formatted_merged

    c['log'] = formatted_log
    return render_to_response('tab_file.html', c,
     context_instance=RequestContext(request, processors=[settings_processor]))
    

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

    # Get a list of files so far generated, by type. Leave off the .yaml
    #  and .xml file extensions, as well as redundancies.
    prec_files = os.listdir(settings.DATA_PATH + 'prec_cont/')
    for i in range(0, len(prec_files)):
        prec_files[i] = prec_files[i][:prec_files[i].rfind('.')]
    prec_files = set(prec_files)
    bal_files = os.listdir(settings.DATA_PATH + 'bal_count_tot/')
    for i in range(0, len(bal_files)):
        bal_files[i] = bal_files[i][:bal_files[i].rfind('.')]
    bal_files = set(bal_files)
    tab_files = os.listdir(settings.DATA_PATH + 'tab_aggr/')
    for i in range(0, len(tab_files)):
        tab_files[i] = tab_files[i][:tab_files[i].rfind('.')]
    tab_files = set(tab_files)
    
    tdg_files = prec_files.union(bal_files)
    merge_files = bal_files.union(tab_files)

    # Get version / last revision info from file
    stream = open('VERSION', 'r')
    version = stream.readlines()

    return Context({'prec_files':prec_files, 'bal_files':bal_files,
                    'tdg_files':tdg_files, 'tab_files':tab_files,
                    'merge_files':merge_files, 'version':version})

def delete_files(files):
    for file in files:
        if os.listdir(settings.DATA_PATH + 'prec_cont/').count(file + '.yaml') == 1:
            os.system('rm -f ' + settings.DATA_PATH + 'prec_cont/' + file + '.*')
        elif os.listdir(settings.DATA_PATH + 'bal_count_tot/').count(file + '.yaml') == 1:
            os.system('rm -f ' + settings.DATA_PATH + 'bal_count_tot/' + file + '.*')                
        else:
            os.system('rm -f ' + settings.DATA_PATH + 'tab_aggr/' + file + '.*')
            os.system('rm -f ' + settings.DATA_PATH + 'reports/' + file + '_report')
    return

def rename_file(data):
    old_name = data['old_name']
    new_name = data['new_name']
    if os.listdir(settings.DATA_PATH + 'prec_cont/').count(old_name + ".yaml") == 1:
        os.rename(settings.DATA_PATH + 'prec_cont/' + old_name + '.yaml',
            settings.DATA_PATH + 'prec_cont/' + new_name + '.yaml')
        os.rename(settings.DATA_PATH + 'prec_cont/' + old_name + '.xml',
            settings.DATA_PATH + 'prec_cont/' + new_name + '.xml')
    elif os.listdir(settings.DATA_PATH + 'bal_count_tot/').count(old_name + ".yaml") == 1:
        os.rename(settings.DATA_PATH + 'bal_count_tot/' + old_name + '.yaml',
            settings.DATA_PATH + 'bal_count_tot/' + new_name + '.yaml')
        os.rename(settings.DATA_PATH + 'bal_count_tot/' + old_name + '.xml',
            settings.DATA_PATH + 'bal_count_tot/' + new_name + '.xml')
    else:
        os.rename(settings.DATA_PATH + 'tab_aggr/' + old_name + '.yaml',
            settings.DATA_PATH + 'tab_aggr/' + new_name + '.yaml')
        os.rename(settings.DATA_PATH + 'tab_aggr/' + old_name + '.xml',
            settings.DATA_PATH + 'tab_aggr/' + new_name + '.xml')
        os.rename(settings.DATA_PATH + 'reports/' + old_name + '_report',
            settings.DATA_PATH + 'reports/' + new_name + '_report')
    return

def settings_processor(request):
    return {'ROOT':settings.SITE_ROOT, 'HOME':settings.LOGIN_URL}
