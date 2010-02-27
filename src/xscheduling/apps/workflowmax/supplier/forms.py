from django.utils.translation import ugettext_lazy as _
from django import forms
from django.forms.widgets import Textarea
from django.utils.text import capfirst
from workflowmax.supplier.models import Supplier

class SupplierForm(forms.Form):
  name = forms.CharField(label = capfirst(_('name')))
  address = forms.CharField(label = capfirst(_('address')), widget=Textarea(), required=False)
  postal_address = forms.CharField(label = capfirst(_('postal address')), widget=Textarea(), required=False)
  phone = forms.CharField(label = capfirst(_('phone')), required=False)
  fax = forms.CharField(label = capfirst(_('fax')), required=False)
  website = forms.URLField(label = capfirst(_('website')), required=False)
  referral_source = forms.CharField(label = capfirst(_('referral source')), required=False)
#  contacts = xml_models.Collection(Contact, order_by="name", xpath="/client/contacts/contact")
#  notes = xml_models.Collection(Note, order_by="title", xpath="/client/notes/note")

#class ContactForm(forms.Form):
#  name = forms.CharField(label = capfirst(_('name')))
#  mobile = forms.CharField(label = capfirst(_('mobile')), required=False)
#  email = forms.CharField(label = capfirst(_('email')), required=False)
#  phone = forms.CharField(label = capfirst(_('phone')), required=False)
#  position = forms.CharField(label = capfirst(_('position')), required=False)


