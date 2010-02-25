from django.contrib import admin
from django.contrib.contenttypes import generic
from client.models import Client, Contact, Note

class ContactInline(admin.StackedInline):
  model = Contact
  extra = 1
  fk_name = "client"

class NoteInline(admin.StackedInline):
  model = Note
  extra = 1
  fk_name = "client"

class ClientAdmin(admin.ModelAdmin):
  inlines = [ContactInline, NoteInline]
  actions_on_bottom = True
  search_fields = ['name']

admin.site.register(Client, ClientAdmin)



