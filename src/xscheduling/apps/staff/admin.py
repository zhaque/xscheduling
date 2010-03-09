from django.contrib import admin
from staff.models import Staff

class StaffAdmin(admin.ModelAdmin):
  actions_on_bottom = True
  search_fields = ['name']

admin.site.register(Staff, StaffAdmin)



