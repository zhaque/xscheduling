from django.contrib import admin
from django.contrib.contenttypes import generic
from supplier.models import Supplier, Contact

class ContactInline(admin.StackedInline):
  model = Contact
  extra = 1
  fk_name = "supplier"

class SupplierAdmin(admin.ModelAdmin):
  inlines = [ContactInline,]
  actions_on_bottom = True
  search_fields = ['name']

admin.site.register(Supplier, SupplierAdmin)
admin.site.register(Contact)



