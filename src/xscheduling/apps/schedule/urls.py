from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'schedule.views.root', name='schedule-root'),
    url(r'^client/$', 'schedule.views.list_clients', name='schedule-client-list'),
    url(r'^client/add/$', 'schedule.views.add_client', name='schedule-client-add'),
    url(r'^client/(?P<object_id>\d+)/$', 'schedule.views.get_client', name='schedule-client'),
    url(r'^client/(?P<object_id>\d+)/edit/$', 'schedule.views.edit_client', name='schedule-client-edit'),
    url(r'^client/(?P<object_id>\d+)/contact/add/$', 'schedule.views.add_client_contact', name='schedule-client-contact-add'),
    url(r'^client/(?P<owner_id>\d+)/contact/(?P<object_id>\d+)/edit/$', 'schedule.views.edit_client_contact', name='schedule-client-contact-edit'),
    url(r'^staff/$', 'schedule.views.list_staff', name='schedule-staff-list'),
    url(r'^staff/add/$', 'schedule.views.add_staff', name='schedule-staff-add'),
    url(r'^staff/(?P<object_id>\d+)/$', 'schedule.views.get_staff', name='schedule-staff'),
    url(r'^staff/(?P<object_id>\d+)/edit/$', 'schedule.views.edit_staff', name='schedule-staff-edit'),
    url(r'^supplier/$', 'schedule.views.list_suppliers', name='schedule-supplier-list'),
    url(r'^supplier/add/$', 'schedule.views.add_supplier', name='schedule-supplier-add'),
    url(r'^supplier/(?P<object_id>\d+)/$', 'schedule.views.get_supplier', name='schedule-supplier'),
    url(r'^supplier/(?P<object_id>\d+)/edit/$', 'schedule.views.edit_supplier', name='schedule-supplier-edit'),
    url(r'^supplier/(?P<object_id>\d+)/contact/add/$', 'schedule.views.add_supplier_contact', name='schedule-supplier-contact-add'),
    url(r'^supplier/(?P<owner_id>\d+)/contact/(?P<object_id>\d+)/edit/$', 'schedule.views.edit_supplier_contact', name='schedule-supplier-contact-edit'),
)
