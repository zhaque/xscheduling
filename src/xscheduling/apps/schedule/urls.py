from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'schedule.views.root', name='schedule-root'),
    url(r'^contacts/$', 'schedule.views.contacts', name='schedule-contacts'),
    url(r'^(?P<client_id>\d+)/$', 'schedule.views.root', name='schedule-client-byid'),
    url(r'^(?P<client_name>[\s\w,.:;]+)/$', 'schedule.views.root', name='schedule-client'),
    url(r'^(?P<client_id>\d+)/edit/$', 'schedule.views.client_edit', name='schedule-client-edit'),
    url(r'^(?P<client_id>\d+)/add_job/$', 'schedule.views.root', {'add_job': True}, name='schedule-client-addjob'),
)
