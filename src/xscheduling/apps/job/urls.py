from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'job.views.list_jobs', name='job-list'),
    url(r'^add/$', 'job.views.add_job', name='job-add'),
    url(r'^(?P<object_id>\d+)/$', 'job.views.get_job', name='job-view'),
    url(r'^(?P<object_id>\d+)/edit/$', 'job.views.edit_job', name='job-edit'),
    url(r'^(?P<object_id>\d+)/delete/$', 'job.views.delete_job', name='job-delete'),
    url(r'^(?P<object_id>\d+)/task/add/$', 'job.views.add_task', name='job-task-add'),
    url(r'^(?P<owner_id>\d+)/task/(?P<object_id>\d+)/edit/$', 'job.views.edit_task', name='job-task-edit'),
    url(r'^(?P<owner_id>\d+)/task/(?P<object_id>\d+)/delete/$', 'job.views.delete_task', name='job-task-delete'),
    url(r'^(?P<object_id>\d+)/milestone/add/$', 'job.views.add_milestone', name='job-milestone-add'),
    url(r'^(?P<owner_id>\d+)/milestone/(?P<object_id>\d+)/edit/$', 'job.views.edit_milestone', name='job-milestone-edit'),
    url(r'^(?P<owner_id>\d+)/milestone/(?P<object_id>\d+)/delete/$', 'job.views.delete_milestone', name='job-milestone-delete'),
    url(r'^(?P<object_id>\d+)/note/add/$', 'job.views.add_note', name='job-note-add'),
    url(r'^(?P<owner_id>\d+)/note/(?P<object_id>\d+)/edit/$', 'job.views.edit_note', name='job-note-edit'),
    url(r'^(?P<owner_id>\d+)/note/(?P<object_id>\d+)/delete/$', 'job.views.delete_note', name='job-note-delete'),
    url(r'^import/$', 'job.views.import_jobs', name='job-import'),
)
