from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'fullcalendar.views.calendar', name='fullcalendar-calendar'),
    url(r'^events/$', 'fullcalendar.views.events', name='fullcalendar-events'),
    url(r'^events/(?P<object_id>\d+)/$', 'fullcalendar.views.events', name='fullcalendar-staff-events'),
)
