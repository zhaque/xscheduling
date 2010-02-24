from django.utils.translation import ugettext_lazy as _
from django import forms
from django.forms.widgets import Textarea
from django.utils.text import capfirst
from workflowmax.staff.models import Staff

class StaffForm(forms.Form):
  name = forms.CharField(label = capfirst(_('name')))
  address = forms.CharField(label = capfirst(_('address')), widget=Textarea(), required=False)
  phone = forms.CharField(label = capfirst(_('phone')), required=False)
  mobile = forms.CharField(label = capfirst(_('mobile')), required=False)
  email = forms.CharField(label = capfirst(_('email')), required=False)
  payrollcode = forms.CharField(label = capfirst(_('payroll code')), required=False)
