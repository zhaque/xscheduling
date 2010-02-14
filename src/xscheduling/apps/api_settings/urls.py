from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'api_settings.views.list_api', name='api_settings-list'),
    url(r'^(?P<object_id>\d+)/enable/$', 'api_settings.views.enable_api', name='api_settings-enable'),
    url(r'^(?P<object_id>\d+)/disable/$', 'api_settings.views.disable_api', name='api_settings-disable'),
)
