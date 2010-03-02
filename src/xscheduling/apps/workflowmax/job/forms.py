from django.utils.translation import ugettext_lazy as _
from django import forms
from django.forms.widgets import Textarea
from django.utils.text import capfirst
from workflowmax.job.models import Job
from workflowmax.client.models import Client

class JobForm(forms.Form):
  name = forms.CharField(label = capfirst(_('name')))
  description = forms.CharField(label = capfirst(_('description')), widget=Textarea())
  start_date = forms.DateField(label = capfirst(_('start date')), input_formats=['%Y%m%d',])
  due_date = forms.DateField(label = capfirst(_('due date')), input_formats=['%Y%m%d',])
  client = forms.ChoiceField(label = capfirst(_('client')), choices=())
  contact = forms.ChoiceField(label = capfirst(_('contact')), choices=(), required=False)
  client_number = forms.CharField(label = capfirst(_('client number')), required=False)
  template_id = forms.CharField(label = capfirst(_('template id')), required=False)

  def __init__(self, *args, **kwargs):
    super(JobForm, self).__init__(*args, **kwargs)

    choices =[]
    clients = Client.objects.all()
    for client in clients:
      choices.append((client.id, client.name))
    self.fields['client'].choices = choices

