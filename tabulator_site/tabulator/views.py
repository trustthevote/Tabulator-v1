import os
import json

from django.template import Context, loader, RequestContext
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest
from django.shortcuts import render_to_response
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

import test_data_generator as TDG
import merger
import audit_header
import tabulator

# Handle requests/responses to and from the welcome template
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
    c = get_file_data()
    return render_to_response('welcome.html', c,
     context_instance=RequestContext(request, processors=[settings_processor]))

# Handle requests/responses to and from the test data generator template
@login_required
def tdg_handler(request):
    # Check to see if the client is posting data
    if request.method == 'POST':
        # Check to see if the client wants to generate a file
        if request.POST.has_key('arguments_tdg'):
            # Get and deserialize the users arguments from JSON
            args = request.POST.getlist('arguments_tdg')
            args = json.loads(args[0])
            
            # Make arguments consistent with where data is stored on the
            #  server, using DATA_PATH from settings.py
            if args[0] == 'jurisdiction' or args[0] == 'contestlist':
                args[1] = settings.DATA_PATH + 'templates/' + args[1]
            elif args[0] == 'counts':
                args[2] = settings.DATA_PATH + 'templates/' + args[2]
                args[3] = settings.DATA_PATH + 'bal_count_tot/' + args[3]
            P = TDG.ProvideRandomBallots(args)  # Make a file
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
    c = get_file_data()
    return render_to_response('tdg.html', c,
     context_instance=RequestContext(request, processors=[settings_processor]))

# Handle requests/responses to and from the merger template
@login_required
def merge_handler(request):
    # Check to see if the client is posting data
    if request.method == 'POST':
        # Check to see if client wants to merge files
        if request.POST.has_key('arguments'):
            # Get and deserialize the users arguments from JSON
            args = request.POST.getlist('arguments')            
            args = json.loads(args[0])
            # Arguments will be made consistent with where data is
            #  stored on the server, as given by DATA_PATH
            args[0] = settings.DATA_PATH + 'templates/' + args[0]

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
            if m.validate() == True:
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
    c = get_file_data()
    return render_to_response('merge.html', c,
     context_instance=RequestContext(request, processors=[settings_processor]))

# Handle requests/responses to and from the tabulator template
@login_required
def tab_handler(request):
    # Check to see if the client is posting data
    if request.method == 'POST':
        # Check to see if client wants to merge files
        if request.POST.has_key('arguments'):
            args = request.POST.getlist('arguments')
            
            args[0] = settings.DATA_PATH + 'tab_aggr/' + args[0]
            args[1] = settings.DATA_PATH + 'templates/' + args[1]

            t = tabulator.Tabulator(args)            
            # Move the reports into the reports/ folder
            os.system('mv ' + args[0] + '_report* ' +
                      settings.DATA_PATH + 'reports/')
            return HttpResponse()
    c = get_file_data()
    return render_to_response('tabulator.html', c,
     context_instance=RequestContext(request, processors=[settings_processor]))

# Read the contents of a requested tdg file from memory, mark it up so
#  that it displays correctly as html, and render it.
@login_required
def tdg_file_handler(request, fname):
    # Check to see if the client is posting data
    if request.method == 'POST':
        # Check to see if the client wants to log the user out
        if request.POST.has_key('logout_user'):
            logout(request)
            return HttpResponse()
    if os.listdir(settings.DATA_PATH + 'templates/').count(fname) == 1:
        stream = open(settings.DATA_PATH + 'templates/' + fname, 'r')
    else:
        stream = open(settings.DATA_PATH + 'bal_count_tot/' + fname, 'r')
    lines = stream.readlines()    
    c = Context({'lines':mark_up(lines)})
    return render_to_response('tdg_file.html', c,
     context_instance=RequestContext(request, processors=[settings_processor]))

# Read the contents of a requested merge file from memory, mark it up so
#  that it displays correctly as html, and render it.
@login_required
def merge_file_handler(request, fname):
    # Check to see if the client is posting data
    if request.method == 'POST':
        # Check to see if the client wants to log the user out
        if request.POST.has_key('logout_user'):
            logout(request)
        return HttpResponse()
    c = Context()
    
    # Read in file data stored on server. A merged file may not have
    #  have been created, but try to load it and format it.
    try:
        stream = open(settings.DATA_PATH + 'tab_aggr/' + fname, 'r')
    except IOError:
        pass
    else:
        c['merged'] = mark_up(stream.readlines())

    fname = fname[:fname.rfind('.')]
    stream = open(settings.DATA_PATH + 'tab_aggr/' + fname + '.log', 'r')    
    c['log'] = mark_up(stream.readlines())

    return render_to_response('merge_file.html', c,
     context_instance=RequestContext(request, processors=[settings_processor]))

# Read the contents of a requested tabulator file from memory, mark it
#  up so that it displays correctly as html, and render it.
@login_required
def tab_file_handler(request, fname):
    # Check to see if the client is posting data
    if request.method == 'POST':
        # Check to see if the client wants to log the user out
        if request.POST.has_key('logout_user'):
            logout(request)
        return HttpResponse()
    stream = open(settings.DATA_PATH + 'reports/' + fname, 'r')
    lines = stream.readlines()
    formatted_lines = []
    
    # If requested file is a .yaml or .xml, fully markup. If not, then
    #  only do a little bit of formatting
    if fname.rfind('.yaml') != -1 or fname.rfind('.xml') != -1:
        formatted_lines = mark_up(lines)
    else:
        for line in lines:
            line = line.replace('\n', '<br/>')
            formatted_lines.append(line.replace(' ', '&nbsp;'))    
    c = Context({'lines':formatted_lines})
    return render_to_response('tab_file.html', c,
     context_instance=RequestContext(request, processors=[settings_processor]))

# Helper function for mark_up. Find the combined number of spaces and
#  dashes that begin a string.
def indent( str ):
    if str == '' or str[:3] == '---':
        return -1
    for i in range( len(str) ):
        if str[i] != ' ' and str[i] != '-':
            return i

# Html-ize the contents of a file so that they display correctly in the
#  front end.
def mark_up( lines ):
    for i in range( len(lines) ):
        lines[i] = lines[i].replace('<', '&lt;')
        lines[i] = lines[i].replace('>', '&gt;')
        lines[i] = lines[i].replace('\t', '   ')
        lines[i] = lines[i].replace('\n', '')
        if i == len(lines) - 1:
            lines[i] = '<li>' + lines[i] + '</li></ul>'
            lines[i] = lines[i].replace(' ', '&nbsp;')
            return lines
        else:
            if indent(lines[i]) == -1 or indent(lines[i]) == indent(lines[i+1]):
                lines[i] = '<li>' + lines[i] + '</li></br>'
            elif indent(lines[i]) > indent(lines[i + 1]):
                lines[i] = '<li>' + lines[i] + '</li></ul></li></br>'
            else:
                lines[i] = '<li><a>' + lines[i] + u' \u25BC</a><ul></br>'
        lines[i] = lines[i].replace(' ', '&nbsp;')

# Get and categorize all the files created by this system, so that a
#  list of them broken down by category can be displayed in the front
#  end.
def get_file_data():
    # Make the subdirectory specified by DATA_PATH within the
    #  directory DATA_PARENT, if it does not exist already. Generated
    #  test data files will go here.    
    if os.listdir(settings.DATA_PARENT).count(settings.DATA_FOLDER) == 0:
        os.mkdir(settings.DATA_PATH)
    if os.listdir(settings.DATA_PATH).count('templates') == 0:
        os.mkdir(settings.DATA_PATH + 'templates/')
    if os.listdir(settings.DATA_PATH).count('bal_count_tot') == 0:
        os.mkdir(settings.DATA_PATH + 'bal_count_tot/')
    if os.listdir(settings.DATA_PATH).count('tab_aggr') == 0:
        os.mkdir(settings.DATA_PATH + 'tab_aggr/')
    if os.listdir(settings.DATA_PATH).count('reports') == 0:
        os.mkdir(settings.DATA_PATH + 'reports/')

    # Get a list of files so far generated, by type. Leave off the .yaml
    #  and .xml file extensions, as well as redundancies.
    templates = os.listdir(settings.DATA_PATH + 'templates/')
    juris_files = []
    prec_files = []
    for i in range(0, len(templates)):
        if templates[i][len(templates[i]) - 5:] == '.yaml':
            s = open(settings.DATA_PATH + 'templates/' + templates[i], 'r')
            a = audit_header.AuditHeader()
            a.load_from_file(s)
            if a.type == 'jurisdiction_slate':
                juris_files.append(templates[i][:len(templates[i]) - 5])
            else:
                prec_files.append(templates[i][:len(templates[i]) - 5])
        templates[i] = templates[i][:templates[i].rfind('.')]
    template_files = set(templates)
    bal_files = os.listdir(settings.DATA_PATH + 'bal_count_tot/')
    for i in range(0, len(bal_files)):
        bal_files[i] = bal_files[i][:bal_files[i].rfind('.')]
    bal_files = set(bal_files)
    tab_files = os.listdir(settings.DATA_PATH + 'tab_aggr/')    
    for i in range(0, len(tab_files)):
        tab_files[i] = tab_files[i][:tab_files[i].rfind('.')]
    no_log_files = []
    for i in tab_files:
        if tab_files.count(i) != 1:
            no_log_files.append(i)
    no_log_files = set(no_log_files)
    tab_files = set(tab_files)
    report_files = os.listdir(settings.DATA_PATH + 'reports/')
    for i in range(0, len(report_files)):
        report_files[i] = report_files[i][:report_files[i].rfind('_report')]
    report_files = set(report_files)

    tdg_files = set(prec_files).union(set(juris_files)).union(bal_files)
    merge_files = bal_files.union(no_log_files)    

    # Get version / last revision info from file
    stream = open('VERSION', 'r')
    version = stream.readlines()

    return Context({'prec_files':prec_files, 'juris_files':juris_files,
                    'bal_files':bal_files, 'tdg_files':tdg_files,
                    'tab_files':tab_files, 'merge_files':merge_files,
                    'report_files':report_files, 'no_log_files': no_log_files,
                    'template_files':template_files, 'version':version})

# Find and delete a list of files that were generated by this system
def delete_files(files):
    for file in files:
        if os.listdir(settings.DATA_PATH + 'reports/').count(file + '_report.csv') == 1:
            os.system('rm -f ' + settings.DATA_PATH + 'reports/' + file + '_report*')
        if os.listdir(settings.DATA_PATH + 'templates/').count(file + '.yaml') == 1:
            os.system('rm -f ' + settings.DATA_PATH + 'templates/' + file + '.*')
        if os.listdir(settings.DATA_PATH + 'bal_count_tot/').count(file + '.yaml') == 1:
            os.system('rm -f ' + settings.DATA_PATH + 'bal_count_tot/' + file + '.*')                
        if os.listdir(settings.DATA_PATH + 'tab_aggr/').count(file + '.yaml') == 1:
            os.system('rm -f ' + settings.DATA_PATH + 'tab_aggr/' + file + '.*')
        if os.listdir(settings.DATA_PATH + 'tab_aggr/').count(file + '.log') == 1:
            os.system('rm -f ' + settings.DATA_PATH + 'tab_aggr/' + file + '.log')
    return

# Find and rename a file that was generated by this system
def rename_file(data):
    old_name = data['old_name']
    new_name = data['new_name']
    if os.listdir(settings.DATA_PATH + 'reports/').count(old_name + "_report.csv") == 1:
        os.rename(settings.DATA_PATH + 'reports/' + old_name + '_report.csv',
            settings.DATA_PATH + 'reports/' + new_name + '_report.csv')
    elif os.listdir(settings.DATA_PATH + 'templates/').count(old_name + ".yaml") == 1:
        os.rename(settings.DATA_PATH + 'templates/' + old_name + '.yaml',
            settings.DATA_PATH + 'templates/' + new_name + '.yaml')
        os.rename(settings.DATA_PATH + 'templates/' + old_name + '.xml',
            settings.DATA_PATH + 'templates/' + new_name + '.xml')
    elif os.listdir(settings.DATA_PATH + 'bal_count_tot/').count(old_name + ".yaml") == 1:
        os.rename(settings.DATA_PATH + 'bal_count_tot/' + old_name + '.yaml',
            settings.DATA_PATH + 'bal_count_tot/' + new_name + '.yaml')
        os.rename(settings.DATA_PATH + 'bal_count_tot/' + old_name + '.xml',
            settings.DATA_PATH + 'bal_count_tot/' + new_name + '.xml')
    else:
        os.rename(settings.DATA_PATH + 'tab_aggr/' + old_name + '.log',
            settings.DATA_PATH + 'tab_aggr/' + new_name + '.log')
        if os.listdir(settings.DATA_PATH + 'tab_aggr/').count(old_name + ".yaml") == 1:
            os.rename(settings.DATA_PATH + 'tab_aggr/' + old_name + '.yaml',
                settings.DATA_PATH + 'tab_aggr/' + new_name + '.yaml')
            os.rename(settings.DATA_PATH + 'tab_aggr/' + old_name + '.xml',
                settings.DATA_PATH + 'tab_aggr/' + new_name + '.xml')
    return

def settings_processor(request):
    return {'ROOT':settings.SITE_ROOT, 'HOME':settings.LOGIN_URL}
