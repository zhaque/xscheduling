from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'workflowmax.views.list_clients', name='workflowmax-list'),
    url(r'^client/(?P<object_id>\d+)/$', 'workflowmax.views.get_client', name='workflowmax-client'),
    url(r'^client/(?P<object_id>\d+)/edit/$', 'workflowmax.views.edit_client', name='workflowmax-client-edit'),
    url(r'^contact/(?P<object_id>\d+)/$', 'workflowmax.views.get_contact', name='workflowmax-contact'),
)
