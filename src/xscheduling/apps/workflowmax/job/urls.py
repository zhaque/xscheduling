from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'workflowmax.job.views.list_jobs', name='workflowmax-job-list'),
    url(r'^add/$', 'workflowmax.job.views.add_job', name='workflowmax-job-add'),
    url(r'^(?P<object_id>\w+)/$', 'workflowmax.job.views.get_job', name='workflowmax-job'),
    url(r'^(?P<object_id>\w+)/edit/$', 'workflowmax.job.views.edit_job', name='workflowmax-job-edit'),
    url(r'^(?P<object_id>\w+)/delete/$', 'workflowmax.job.views.delete_job', name='workflowmax-job-delete'),
    url(r'^(?P<object_id>\w+)/note/add/$', 'workflowmax.job.views.add_job_note', name='workflowmax-job-note-add'),
    url(r'^(?P<owner_id>\w+)/task/(?P<object_id>\d+)/edit/$', 'workflowmax.job.views.edit_job_task', name='workflowmax-job-task-edit'),
)
