from django.utils.translation import ugettext_lazy as _
from django import forms
from job.models import Job

class JobForm(forms.ModelForm):
  class Meta:
    model = Job
    exclude = ('wm_id')
