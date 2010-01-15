from django.conf.urls.defaults import *
import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',    
    (r'^static/(?P<path>.*)$', 'django.views.static.serve',
     {'document_root':  settings.MEDIA_ROOT}),

    (r'^$', 'tabulator.views.welcome_handler'),
    (r'^welcome/?$', 'tabulator.views.welcome_handler'),
    (r'^tdg/?$', 'tabulator.views.tdg_handler'),
    (r'^merger/?$', 'tabulator.views.merge_handler'),
    (r'^tabulator/?$', 'tabulator.views.tab_handler'),
    (r'^data/tdg/(?P<fname>.*)$', 'tabulator.views.tdg_file_handler'),
    (r'^data/merge/(?P<fname>.*)$', 'tabulator.views.merge_file_handler'),
    (r'^data/tabulator/(?P<fname>.*)$', 'tabulator.views.tab_file_handler'),
    (r'^download/(?P<file_and_parent>.*)$', 'tabulator.views.download_handler'),
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/(.*)', include(admin.site.urls)),
)
