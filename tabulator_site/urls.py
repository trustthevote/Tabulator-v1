from django.conf.urls.defaults import *
import settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',    
    (r'^static/(?P<path>.*)$', 'django.views.static.serve',
     {'document_root':  settings.MEDIA_ROOT}),
    (r'^welcome$', 'tabulator.views.welcome_handler'),
    (r'^tdg$', 'tabulator.views.tdg_handler'),
    (r'^tabulator$', 'tabulator.views.tab_handler'),
    (r'^file$', 'tabulator.views.file_handler'),
    #(r'^$', 'tabulator.views.default_handler'),
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    #(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    #(r'^admin/(.*)', admin.site.root),
)
