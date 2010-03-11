from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'job.views.list_jobs', name='job-list'),
    url(r'^add/$', 'job.views.add_job', name='job-add'),
    url(r'^(?P<object_id>\d+)/$', 'job.views.get_job', name='job-view'),
    url(r'^(?P<object_id>\d+)/edit/$', 'job.views.edit_job', name='job-edit'),
    url(r'^(?P<object_id>\d+)/delete/$', 'job.views.delete_job', name='job-delete'),
#    url(r'^(?P<object_id>\d+)/contact/add/$', 'client.views.add_contact', name='client-contact-add'),
#    url(r'^(?P<owner_id>\d+)/contact/(?P<object_id>\d+)/edit/$', 'client.views.edit_contact', name='client-contact-edit'),
#    url(r'^(?P<object_id>\d+)/note/add/$', 'client.views.add_note', name='client-note-add'),
#    url(r'^(?P<owner_id>\d+)/note/(?P<object_id>\d+)/$', 'client.views.get_note', name='client-note-view'),
#    url(r'^(?P<owner_id>\d+)/note/(?P<object_id>\d+)/edit/$', 'client.views.edit_note', name='client-note-edit'),
    url(r'^import/$', 'job.views.import_jobs', name='job-import'),
)
