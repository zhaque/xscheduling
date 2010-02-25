from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'schedule.views.root', name='schedule-root'),
    url(r'^client/$', 'schedule.views.list_clients', name='schedule-client-list'),
    url(r'^client/add/$', 'schedule.views.add_client', name='schedule-client-add'),
    url(r'^client/(?P<object_id>\d+)/$', 'schedule.views.get_client', name='schedule-client'),
    url(r'^client/(?P<object_id>\d+)/edit/$', 'schedule.views.edit_client', name='schedule-client-edit'),
    url(r'^client/(?P<object_id>\d+)/contact/add/$', 'schedule.views.add_contact', name='schedule-contact-add'),
    url(r'^contact/(?P<object_id>\d+)/$', 'schedule.views.get_contact', name='schedule-contact'),
    url(r'^contact/(?P<object_id>\d+)/edit/$', 'schedule.views.edit_contact', name='schedule-contact-edit'),
    url(r'^staff/$', 'schedule.views.list_staff', name='schedule-staff-list'),
    url(r'^staff/add/$', 'schedule.views.add_staff', name='schedule-staff-add'),
    url(r'^staff/(?P<object_id>\d+)/$', 'schedule.views.get_staff', name='schedule-staff'),
    url(r'^staff/(?P<object_id>\d+)/edit/$', 'schedule.views.edit_staff', name='schedule-staff-edit'),
)
