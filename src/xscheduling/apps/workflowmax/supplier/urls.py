from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'workflowmax.supplier.views.list_suppliers', name='workflowmax-supplier-list'),
    url(r'^add/$', 'workflowmax.supplier.views.add_supplier', name='workflowmax-supplier-add'),
    url(r'^(?P<object_id>\d+)/$', 'workflowmax.supplier.views.get_supplier', name='workflowmax-supplier'),
    url(r'^(?P<object_id>\d+)/edit/$', 'workflowmax.supplier.views.edit_supplier', name='workflowmax-supplier-edit'),
    url(r'^(?P<object_id>\d+)/delete/$', 'workflowmax.supplier.views.delete_supplier', name='workflowmax-supplier-delete'),
    url(r'^(?P<object_id>\d+)/contact/add/$', 'workflowmax.supplier.views.add_supplier_contact', name='workflowmax-supplier-contact-add'),
    url(r'^(?P<owner_id>\d+)/contact/(?P<object_id>\d+)/edit/$', 'workflowmax.supplier.views.edit_supplier_contact', name='workflowmax-supplier-contact-edit'),
)
