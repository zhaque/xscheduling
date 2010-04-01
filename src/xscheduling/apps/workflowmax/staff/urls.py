from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'workflowmax.staff.views.list_staff', name='workflowmax-staff-list'),
    url(r'^add/$', 'workflowmax.staff.views.add_staff', name='workflowmax-staff-add'),
    url(r'^(?P<object_id>\d+)/$', 'workflowmax.staff.views.get_staff', name='workflowmax-staff'),
    url(r'^(?P<object_id>\d+)/edit/$', 'workflowmax.staff.views.edit_staff', name='workflowmax-staff-edit'),
    url(r'^(?P<object_id>\d+)/delete/$', 'workflowmax.staff.views.delete_staff', name='workflowmax-staff-delete'),
    url(r'^(?P<object_id>\d+)/jobs/$', 'workflowmax.staff.views.get_staff_jobs', name='workflowmax-staff-jobs'),
)
