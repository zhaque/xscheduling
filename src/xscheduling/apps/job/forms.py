from django.utils.translation import ugettext_lazy as _
from django import forms
from job.models import Job, Task, Milestone, Note

class AddJobForm(forms.ModelForm):
  class Meta:
    model = Job
    exclude = ('wm_id')

class EditJobForm(forms.ModelForm):
  class Meta:
    model = Job
#    exclude = ('wm_id')
    fields = ('state', 'staff')

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
