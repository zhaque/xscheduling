from django.contrib import admin
from api_settings.models import Api

class ApiAdmin(admin.ModelAdmin):
  list_display = ('name', 'uri', 'api_key', 'user', 'enabled', 'optional',)
  list_filter = ['user', 'enabled', 'optional',]
  
admin.site.register(Api, ApiAdmin)
