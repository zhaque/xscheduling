from django.contrib import admin
from staff.models import Staff, Skill

class StaffAdmin(admin.ModelAdmin):
  actions_on_bottom = True
  search_fields = ['name']

admin.site.register(Staff, StaffAdmin)
admin.site.register(Skill)



