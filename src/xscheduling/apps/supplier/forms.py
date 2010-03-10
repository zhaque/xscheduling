from django.utils.translation import ugettext_lazy as _
from django import forms
from supplier.models import Supplier, Contact

class SupplierForm(forms.ModelForm):
  class Meta:
    model = Supplier
    exclude = ('address', 'postal_address', 'wm_id')

class ContactForm(forms.ModelForm):
  class Meta:
    model = Contact
    exclude = ('supplier', 'wm_id')
