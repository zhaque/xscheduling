from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
    url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}, name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'template_name': 'logout.html'}, name='logout'),
    url(r'^api-settings/', include('api_settings.urls')),
    url(r'^schedule/', include('schedule.urls')),
    url(r'^', 'django.views.generic.simple.redirect_to', { 'url': '/schedule/client/'}),
)
