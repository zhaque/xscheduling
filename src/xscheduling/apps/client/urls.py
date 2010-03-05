from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'client.views.list_clients', name='client-list'),
    url(r'^add/$', 'client.views.add_client', name='client-add'),
    url(r'^(?P<object_id>\d+)/$', 'client.views.get_client', name='client-view'),
    url(r'^(?P<object_id>\d+)/edit/$', 'client.views.edit_client', name='client-edit'),
    url(r'^(?P<object_id>\d+)/contact/add/$', 'client.views.add_contact', name='client-contact-add'),
    url(r'^(?P<owner_id>\d+)/contact/(?P<object_id>\d+)/edit/$', 'client.views.edit_contact', name='client-contact-edit'),
    url(r'^(?P<object_id>\d+)/note/add/$', 'client.views.add_note', name='client-note-add'),
    url(r'^(?P<owner_id>\d+)/note/(?P<object_id>\d+)/$', 'client.views.get_note', name='client-note-view'),
    url(r'^(?P<owner_id>\d+)/note/(?P<object_id>\d+)/edit/$', 'client.views.edit_note', name='client-note-edit'),
)
