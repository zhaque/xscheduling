from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'staff.views.list_staff', name='staff-list'),
    url(r'^add/$', 'staff.views.add_staff', name='staff-add'),
    url(r'^(?P<object_id>\d+)/$', 'staff.views.get_staff', name='staff-view'),
    url(r'^(?P<object_id>\d+)/edit/$', 'staff.views.edit_staff', name='staff-edit'),
    url(r'^(?P<object_id>\d+)/delete/$', 'staff.views.delete_staff', name='staff-delete'),
    url(r'^(?P<object_id>\d+)/jobs/$', 'staff.views.get_staff_jobs', name='staff-jobs'),
    url(r'^import/$', 'staff.views.import_staff', name='staff-import'),
)
