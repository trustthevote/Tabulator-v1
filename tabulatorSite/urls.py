from django.conf.urls.defaults import *
import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',    
    (r'^tdg/$', 'tabulatorSite.testDataGenerator.views.TDGhome'),
	(r'^tabulator/$', 'tabulatorSite.tabulator.views.tabulatorHome'),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    #(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    #(r'^admin/(.*)', admin.site.root),
)

#The following is used to serve up local media files like images
#if settings.LOCAL_DEV:
baseurlregex = r'^static/(?P<path>.*)$'
urlpatterns += patterns('',
    (baseurlregex, 'django.views.static.serve', {'document_root':  settings.MEDIA_ROOT}),)
