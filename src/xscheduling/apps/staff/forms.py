from django.utils.translation import ugettext_lazy as _
from django import forms

from staff.models import Staff

class StaffForm(forms.ModelForm):
  class Meta:
    model = Staff
    exclude = ('address', 'wm_id')
