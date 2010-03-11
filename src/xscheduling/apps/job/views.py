from datetime import datetime, timedelta
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _
from django.utils.text import capfirst
from django.views.generic.create_update import delete_object
from django.views.generic.simple import direct_to_template

from uni_form.helpers import FormHelper, Submit, Reset

from client.models import Client, Address
from job.forms import JobForm
from job.models import Job, Task, Milestone, JobState, JobType
from workflowmax.job.models import Job as WorkflowmaxJob

def list_jobs(request):
  context_vars = dict()
  context_vars['header'] = capfirst(_('jobs'))
  context_vars['jobs'] = Job.objects.all()
  return direct_to_template(request, template='job/list.html', extra_context=context_vars)

def get_job(request, object_id):
  context_vars = dict()
  try:
    object_id = int(object_id)
  except ValueError:
    return HttpResponseRedirect(reverse('job-list'))
  job = Job.objects.get(id=object_id)
  context_vars['header'] = capfirst(_('job %s') % job.name)
  context_vars['job'] = job
  return direct_to_template(request, template='job/view.html', extra_context=context_vars)

def add_job(request):
  context_vars = dict()
  context_vars['header'] = capfirst(_('add new job'))
  job_form = JobForm()
  helper = FormHelper()
  helper.form_class = 'uniform'
  submit = Submit('save',_('save'))
  helper.add_input(submit)
  if request.method == "POST":
    job_form = JobForm(request.POST, request.FILES)
    if job_form.is_valid():
      job = job_form.save()
      if settings.WORKFLOWMAX_APIKEY and settings.WORKFLOWMAX_ACCOUNTKEY:
        job.wm_sync()
      return HttpResponseRedirect(reverse('job-view', args=[job.id]))
  
  context_vars['form'] = job_form
  context_vars['helper'] = helper
  return direct_to_template(request, template='job/uniform.html', extra_context=context_vars)

def edit_job(request, object_id):
  pass

def delete_job(request, object_id):
  context_vars = dict()
  try:
    object_id = int(object_id)
    job = Job.objects.get(id=object_id)
  except ValueError, ObjectDoesNotExist:
    return HttpResponseRedirect(reverse('job-list'))

  if request.method == 'POST' and settings.WORKFLOWMAX_APIKEY and settings.WORKFLOWMAX_ACCOUNTKEY:
    job.wm_delete()
  
  return delete_object(request, object_id=job.id, model=Job, login_required=True, template_name='job/delete.html', post_delete_redirect=reverse('job-list'), extra_context={'header': capfirst(_('delete job')), 'comment': capfirst(_('you are trying to delete job "%s". Sure?') % job.name)})

def import_jobs(request):
  context_vars = dict()
  context_vars['header'] = capfirst(_('import jobs from workflowmax'))
  context_vars['comment'] = capfirst(_('this will destroy all your local jobs, please confirm your decision.'))
  if request.method == "POST":
    for job in Job.objects.all():
      job.delete()
    wm_jobs = WorkflowmaxJob.objects.all(datetime.now() - timedelta(days=365), datetime.now())
#    wm_jobs = WorkflowmaxJob.objects.current()
    for wm_job in wm_jobs:
      job = Job()
      job.wm_import(wm_job)
    return HttpResponseRedirect(reverse('job-list'))
  
  return direct_to_template(request, template='job/import.html', extra_context=context_vars)
  

