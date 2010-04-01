from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.text import capfirst
from django.utils.translation import ugettext as _
from django.views.generic.simple import direct_to_template
from uni_form.helpers import FormHelper, Submit, Reset
from workflowmax.client.models import Client, Contact
from workflowmax.client.forms import ClientForm, ContactForm
from workflowmax.exceptions import ResponseStatusError
from workflowmax.job.models import Job, Note, Task
from workflowmax.job.forms import AddJobForm, EditJobForm, NoteForm, TaskForm
from workflowmax.staff.models import Staff
from workflowmax.staff.forms import StaffForm
from workflowmax.supplier.models import Supplier, Contact as SupplierContact
from workflowmax.supplier.forms import SupplierForm

try:
  from xml.etree import ElementTree # for Python 2.5 users
except ImportError:
  from elementtree import ElementTree
import gdata.calendar.service
import gdata.service
import atom.service
import gdata.calendar
import atom
import atom.token_store
import atom.http_interface
import getopt
import sys
import string
import time
from datetime import datetime

#Job views
@login_required
def list_jobs(request):
  context_vars = dict()
  context_vars['header'] = capfirst(_('current job list'))
  context_vars['jobs'] = Job.objects.current()
  return direct_to_template(request, template='workflowmax/list.html', extra_context=context_vars)

@login_required
def get_job(request, object_id):
  context_vars = dict()
  context_vars['header'] = '%s %s' % (capfirst(_('job')), object_id)
  context_vars['job'] = Job.objects.get(id=object_id)
  return direct_to_template(request, template='workflowmax/view.html', extra_context=context_vars)
  
@login_required
def add_job(request):
  context_vars = dict()
  context_vars['header'] = capfirst(_('add new job'))
  form = AddJobForm()
  helper = FormHelper()
  helper.form_class = 'uniform'
  submit = Submit('save',_('save'))
  helper.add_input(submit)
  if request.method == "POST":
    form = AddJobForm(request.POST, request.FILES)
    if form.is_valid():
      job = Job()
      job.name = form.cleaned_data['name']
      job.description = form.cleaned_data['description']
      job.start_date = strptime(form.cleaned_data['start_date'], '%Y%m%d')
      job.due_date = strptime(form.cleaned_data['due_date'], '%Y%m%d')
      client_id = form.cleaned_data['client']
      client = Client.objects.get(id=client_id)
      job.clients = [client,]
      job = job.save()
      return HttpResponseRedirect(reverse('workflowmax-job', args=[job.id]))
  
  context_vars['form'] = form
  context_vars['helper'] = helper
  return direct_to_template(request, template='workflowmax/form.html', extra_context=context_vars)

@login_required
def edit_job(request, object_id):
  context_vars = dict()
  context_vars['header'] = '%s %s' % (capfirst(_('job')), object_id)
  job = Job.objects.get(id=object_id)
  form = EditJobForm(job.to_dict())
  helper = FormHelper()
  helper.form_class = 'uniform'
  submit = Submit('save',_('save'))
  helper.add_input(submit)
  if request.method == "POST":
    form = EditJobForm(request.POST, request.FILES)
    if form.is_valid():
      job.state = form.cleaned_data['state']
      if form.cleaned_data['assigned']:
        job.assigned = []
        for assigned_id in form.cleaned_data['assigned']:
          try:
            job.assigned.append(Staff.objects.get(id=assigned_id))
          except ResponseStatusError:
            pass
      job.save()
      return HttpResponseRedirect(reverse('workflowmax-job', args=[job.id]))
  
  context_vars['form'] = form
  context_vars['helper'] = helper
  return direct_to_template(request, template='workflowmax/form.html', extra_context=context_vars)

@login_required
def delete_job(request, object_id):
  context_vars = dict()
  context_vars['header'] = '%s %s' % (capfirst(_('delete job')), object_id)
  context_vars['comment'] = _('You are trying to delete job "%s". Sure?') % object_id
  job = Job.objects.get(id=object_id)
  
  if request.method == "POST":
    job.delete()
    return HttpResponseRedirect(reverse('workflowmax-job-list'))

  return direct_to_template(request, template='workflowmax/delete.html', extra_context=context_vars)

@login_required
def add_job_note(request, object_id):
  job = Job.objects.get(id=object_id)
  context_vars = dict()
  context_vars['header'] = capfirst(_('add new note for job %s') % job.id)
  form = NoteForm()
  helper = FormHelper()
  helper.form_class = 'uniform'
  submit = Submit('save',_('save'))
  helper.add_input(submit)
  if request.method == "POST":
    form = NoteForm(request.POST, request.FILES)
    if form.is_valid():
      note = Note()
      note.owner_id = job.id
      note.title = form.cleaned_data['title']
      note.text = form.cleaned_data['text']
      note.folder = form.cleaned_data['folder']
      note.public = form.cleaned_data['public']
      note.save()
      return HttpResponseRedirect(reverse('workflowmax-job', args=[job.id]))
  context_vars['form'] = form
  context_vars['helper'] = helper
  
  return direct_to_template(request, template='workflowmax/form.html', extra_context=context_vars)

@login_required
def edit_job_task(request, owner_id, object_id):
  try:
    object_id = int(object_id)
  except ValueError:
    return HttpResponseRedirect(reverse('workflowmax-job', args=[owner_id]))
  context_vars = dict()
  context_vars['header'] = capfirst(_('edit task %d') % object_id)
#  task = Task.objects.get(id=object_id)
  job = Job.objects.get(id=owner_id)
  for task_obj in job.tasks:
    if task_obj.id == object_id:
      task = task_obj
  if not task:
    return HttpResponseRedirect(reverse('workflowmax-job', args=[owner_id]))

  task = Task(xml_object=task)
  form = TaskForm(task.to_dict())
  helper = FormHelper()
  submit = Submit('save',_('save'))
  helper.add_input(submit)
  if request.method == "POST":
    form = TaskForm(request.POST, request.FILES)
    if form.is_valid():
      task.owner_id = job.id
      task.name = form.cleaned_data['name']
      task.description = form.cleaned_data['description']
      task.estimated_minutes = form.cleaned_data['estimated_minutes']
#      task.actual_minutes = form.cleaned_data['actual_minutes']
#      task.completed = form.cleaned_data['completed']
#      task.billable = form.cleaned_data['billable']
#      task.start_date = form.cleaned_data['start_date']
#      task.due_date = form.cleaned_data['due_date']
#      task.completed = form.cleaned_data['completed']
#      if form.cleaned_data['assigned']:
#        task.assigned = []
#        for assigned_id in form.cleaned_data['assigned']:
#          try:
#            task.assigned.append(Staff.objects.get(id=assigned_id))
#          except ResponseStatusError:
#            pass
      task.save()
      return HttpResponseRedirect(reverse('workflowmax-job', args=[owner_id]))
  
  context_vars['form'] = form
  context_vars['helper'] = helper
  return direct_to_template(request, template='workflowmax/form.html', extra_context=context_vars)



