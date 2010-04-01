from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'workflowmax.views.root', name='workflowmax-root'),
    url(r'^client/', include('workflowmax.client.urls')),
    url(r'^staff/', include('workflowmax.staff.urls')),
    url(r'^supplier/', include('workflowmax.supplier.urls')),
    url(r'^job/', include('workflowmax.job.urls')),
)
