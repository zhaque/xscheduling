from django.utils.translation import ugettext_lazy as _
from django import forms
from django.forms.widgets import Textarea
from django.utils.text import capfirst
from workflowmax.job.models import Job, Note
from workflowmax.client.models import Client
from workflowmax.staff.models import Staff

class AddJobForm(forms.Form):
  name = forms.CharField(label = capfirst(_('name')))
  description = forms.CharField(label = capfirst(_('description')), widget=Textarea())
  start_date = forms.DateField(label = capfirst(_('start date')), input_formats=['%Y%m%d',])
  due_date = forms.DateField(label = capfirst(_('due date')), input_formats=['%Y%m%d',])
  client = forms.ChoiceField(label = capfirst(_('client')), choices=())
#  contact = forms.ChoiceField(label = capfirst(_('contact')), choices=(), required=False)
  client_number = forms.CharField(label = capfirst(_('client number')), required=False)
  template_id = forms.CharField(label = capfirst(_('template id')), required=False)

  def __init__(self, *args, **kwargs):
    super(AddJobForm, self).__init__(*args, **kwargs)

    choices =[]
    clients = Client.objects.all()
    for client in clients:
      choices.append((client.id, client.name))
    self.fields['client'].choices = choices

class EditJobForm(forms.Form):
  state = forms.CharField(label = capfirst(_('state')), required=False)
  assigned = forms.MultipleChoiceField(label = capfirst(_('assigned to')), choices=(), required=False)

  def __init__(self, *args, **kwargs):
    super(EditJobForm, self).__init__(*args, **kwargs)

    choices =[]
    staff_list = Staff.objects.all()
    for staff in staff_list:
      choices.append((staff.id, staff.name))
    self.fields['assigned'].choices = choices

class NoteForm(forms.Form):
  title = forms.CharField(label = capfirst(_('title')))
  text = forms.CharField(label = capfirst(_('text')))
  folder = forms.CharField(label = capfirst(_('folder')), required=False)
  public = forms.BooleanField(label = capfirst(_('public')), required=False)

class TaskForm(forms.Form):
  name = forms.CharField(label = capfirst(_('name')))
  description = forms.CharField(label = capfirst(_('description')), widget=Textarea(), required=False)
  estimated_minutes = forms.IntegerField(label = capfirst(_('estimated minutes')), required=False)




