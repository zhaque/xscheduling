from django.contrib.admin.widgets import AdminSplitDateTime
from django.utils.translation import ugettext_lazy as _
from django import forms
from job.models import Job, Task, Milestone, Note

class AddJobForm(forms.ModelForm):
  class Meta:
    model = Job
    exclude = ('wm_id', 'state', 'name')

  def __init__(self, *args, **kwargs):
    super(AddJobForm, self).__init__(*args, **kwargs)
    self.fields['start_date'].widget = AdminSplitDateTime()
    self.fields['due_date'].widget = AdminSplitDateTime()

class EditJobForm(forms.ModelForm):
  class Meta:
    model = Job
#    exclude = ('wm_id')
    fields = ('state', 'staff', 'suppliers')

class TaskForm(forms.ModelForm):
  class Meta:
    model = Task
    exclude = ('wm_id', 'job')

class MilestoneForm(forms.ModelForm):
  class Meta:
    model = Milestone
    exclude = ('job')

class NoteForm(forms.ModelForm):
  class Meta:
    model = Note
    exclude = ('job')
