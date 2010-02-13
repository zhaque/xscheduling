from django.utils.translation import ugettext_lazy as _
from django import forms
from api_settings.models import Api

class ApiAdminForm(forms.ModelForm):
  class Meta:
    model = Api
