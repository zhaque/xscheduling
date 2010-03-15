from django.utils.translation import ugettext_lazy as _
from django import forms

from staff.models import Staff

class StaffForm(forms.ModelForm):
  class Meta:
    model = Staff
    exclude = ('first_name', 'last_name', 'is_staff', 'is_active', 'is_superuser', 'password', 'last_login', 'date_joined', 'groups', 'user_permissions', 'address', 'wm_id')
