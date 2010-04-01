from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'schedule.views.root', name='schedule-root'),
    url(r'^contacts/$', 'schedule.views.contacts', name='schedule-contacts'),
)
