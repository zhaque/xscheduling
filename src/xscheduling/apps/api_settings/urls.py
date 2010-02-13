from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'api_settings.views.list_api', name='api_settings-list'),
)
