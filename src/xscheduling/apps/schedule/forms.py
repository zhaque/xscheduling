from django.contrib.admin.widgets import AdminSplitDateTime
from django.utils.translation import ugettext_lazy as _
from django import forms

from client.models import Client, Address
from job.forms import AddJobForm as BaseAddJobForm
from job.models import Job


class ClientForm(forms.ModelForm):
  class Meta:
    model = Client
    exclude = ('address', 'postal_address', 'wm_id', 'email', 'fax', 'website')

class AddressForm(forms.ModelForm):
  class Meta:
    model = Address
    exclude = ('latitude', 'longitude', 'county', 'country')

class AddJobForm(BaseAddJobForm):
  class Meta:
    model = Job
    exclude = ('wm_id', 'state', 'suppliers', 'client', 'name')

class EditJobForm(forms.ModelForm):
  class Meta:
    model = Job
    fields = ('state', 'staff')
