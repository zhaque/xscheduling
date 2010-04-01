from django.conf.urls.defaults import *
from django.conf import settings

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
    url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}, name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'template_name': 'logout.html'}, name='logout'),
    url(r'^api-settings/', include('api_settings.urls')),
    url(r'^workflowmax/', include('workflowmax.urls')),
    url(r'^schedule/', include('schedule.urls')),
    url(r'^client/', include('client.urls')),
    url(r'^staff/', include('staff.urls')),
    url(r'^supplier/', include('supplier.urls')),
    url(r'^job/', include('job.urls')),
    url(r'^calendar/', include('fullcalendar.urls')),
    url(r'^$', 'django.views.generic.simple.redirect_to', { 'url': '/schedule/'}),
)

# serve static files in debug mode
if settings.SERVE_MEDIA:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )
