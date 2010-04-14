from django.contrib.admin.widgets import AdminSplitDateTime
from django.utils.translation import ugettext_lazy as _
from django import forms

from client.models import Client, Address
from job.models import Job


class ClientForm(forms.ModelForm):
  class Meta:
    model = Client
    exclude = ('address', 'postal_address', 'wm_id', 'email', 'fax', 'website')

class AddressForm(forms.ModelForm):
  class Meta:
    model = Address
    exclude = ('latitude', 'longitude', 'county', 'country')

class AddJobForm(forms.ModelForm):
  class Meta:
    model = Job
#    fields = ('type', 'description')
    exclude = ('wm_id', 'state', 'suppliers', 'client', 'name')

  def __init__(self, *args, **kwargs):
    super(AddJobForm, self).__init__(*args, **kwargs)
    self.fields['start_date'].widget = AdminSplitDateTime()
    self.fields['due_date'].widget = AdminSplitDateTime()

class EditJobForm(forms.ModelForm):
  class Meta:
    model = Job
#    exclude = ('wm_id')
    fields = ('state', 'staff')
