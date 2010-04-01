from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'workflowmax.client.views.list_clients', name='workflowmax-client-list'),
    url(r'^add/$', 'workflowmax.client.views.add_client', name='workflowmax-client-add'),
    url(r'^(?P<object_id>\d+)/$', 'workflowmax.client.views.get_client', name='workflowmax-client'),
    url(r'^(?P<object_id>\d+)/edit/$', 'workflowmax.client.views.edit_client', name='workflowmax-client-edit'),
    url(r'^(?P<object_id>\d+)/delete/$', 'workflowmax.client.views.delete_client', name='workflowmax-client-delete'),
    url(r'^(?P<object_id>\d+)/contact/add/$', 'workflowmax.client.views.add_client_contact', name='workflowmax-client-contact-add'),
    url(r'^(?P<owner_id>\d+)/contact/(?P<object_id>\d+)/edit/$', 'workflowmax.client.views.edit_client_contact', name='workflowmax-client-contact-edit'),
)
