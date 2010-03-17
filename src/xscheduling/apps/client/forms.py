from django.utils.translation import ugettext_lazy as _
from django import forms

from client.models import Client, Contact, Note, Address

class ClientForm(forms.ModelForm):
  class Meta:
    model = Client
    exclude = ('address', 'postal_address', 'wm_id')

class ContactForm(forms.ModelForm):
  class Meta:
    model = Contact
    exclude = ('client', 'wm_id')

class NoteForm(forms.ModelForm):
  class Meta:
    model = Note

class AddressForm(forms.ModelForm):
  class Meta:
    model = Address
    exclude = ('latitude', 'longitude')

ContactFormSet = forms.formsets.formset_factory(ContactForm)

class InvalidForm(Exception):
  """ Invalid form exception. """