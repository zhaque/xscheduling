from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'schedule.views.root', name='schedule-root'),
    url(r'^client/$', 'schedule.views.list_clients', name='schedule-client-list'),
    url(r'^client/add/$', 'schedule.views.add_client', name='schedule-client-add'),
    url(r'^client/(?P<object_id>\d+)/$', 'schedule.views.get_client', name='schedule-client'),
    url(r'^client/(?P<object_id>\d+)/edit/$', 'schedule.views.edit_client', name='schedule-client-edit'),
    url(r'^client/(?P<object_id>\d+)/delete/$', 'schedule.views.delete_client', name='schedule-client-delete'),
    url(r'^client/(?P<object_id>\d+)/contact/add/$', 'schedule.views.add_client_contact', name='schedule-client-contact-add'),
    url(r'^client/(?P<owner_id>\d+)/contact/(?P<object_id>\d+)/edit/$', 'schedule.views.edit_client_contact', name='schedule-client-contact-edit'),
    url(r'^staff/$', 'schedule.views.list_staff', name='schedule-staff-list'),
    url(r'^staff/add/$', 'schedule.views.add_staff', name='schedule-staff-add'),
    url(r'^staff/(?P<object_id>\d+)/$', 'schedule.views.get_staff', name='schedule-staff'),
    url(r'^staff/(?P<object_id>\d+)/edit/$', 'schedule.views.edit_staff', name='schedule-staff-edit'),
    url(r'^staff/(?P<object_id>\d+)/delete/$', 'schedule.views.delete_staff', name='schedule-staff-delete'),
    url(r'^staff/(?P<object_id>\d+)/jobs/$', 'schedule.views.get_staff_jobs', name='schedule-staff-jobs'),
    url(r'^supplier/$', 'schedule.views.list_suppliers', name='schedule-supplier-list'),
    url(r'^supplier/add/$', 'schedule.views.add_supplier', name='schedule-supplier-add'),
    url(r'^supplier/(?P<object_id>\d+)/$', 'schedule.views.get_supplier', name='schedule-supplier'),
    url(r'^supplier/(?P<object_id>\d+)/edit/$', 'schedule.views.edit_supplier', name='schedule-supplier-edit'),
    url(r'^supplier/(?P<object_id>\d+)/delete/$', 'schedule.views.delete_supplier', name='schedule-supplier-delete'),
    url(r'^supplier/(?P<object_id>\d+)/contact/add/$', 'schedule.views.add_supplier_contact', name='schedule-supplier-contact-add'),
    url(r'^supplier/(?P<owner_id>\d+)/contact/(?P<object_id>\d+)/edit/$', 'schedule.views.edit_supplier_contact', name='schedule-supplier-contact-edit'),
    url(r'^job/$', 'schedule.views.list_jobs', name='schedule-job-list'),
    url(r'^job/add/$', 'schedule.views.add_job', name='schedule-job-add'),
    url(r'^job/(?P<object_id>\w+)/$', 'schedule.views.get_job', name='schedule-job'),
    url(r'^job/(?P<object_id>\w+)/edit/$', 'schedule.views.edit_job', name='schedule-job-edit'),
    url(r'^job/(?P<object_id>\w+)/delete/$', 'schedule.views.delete_job', name='schedule-job-delete'),
    url(r'^job/(?P<object_id>\w+)/note/add/$', 'schedule.views.add_job_note', name='schedule-job-note-add'),
    url(r'^job/(?P<owner_id>\w+)/task/(?P<object_id>\d+)/edit/$', 'schedule.views.edit_job_task', name='schedule-job-task-edit'),
)
