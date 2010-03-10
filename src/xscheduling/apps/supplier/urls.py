from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'supplier.views.list_suppliers', name='supplier-list'),
    url(r'^add/$', 'supplier.views.add_supplier', name='supplier-add'),
    url(r'^(?P<object_id>\d+)/$', 'supplier.views.get_supplier', name='supplier-view'),
    url(r'^(?P<object_id>\d+)/edit/$', 'supplier.views.edit_supplier', name='supplier-edit'),
    url(r'^(?P<object_id>\d+)/delete/$', 'supplier.views.delete_supplier', name='supplier-delete'),
    url(r'^(?P<object_id>\d+)/contact/add/$', 'supplier.views.add_contact', name='supplier-contact-add'),
    url(r'^(?P<owner_id>\d+)/contact/(?P<object_id>\d+)/edit/$', 'supplier.views.edit_contact', name='supplier-contact-edit'),
    url(r'^import/$', 'supplier.views.import_suppliers', name='supplier-import'),
)
