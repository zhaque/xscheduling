from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _
from django.utils.text import capfirst
from django.views.generic.create_update import delete_object
from django.views.generic.simple import direct_to_template

from uni_form.helpers import FormHelper, Submit, Reset, Layout, HTML, Row

from client.models import Client, Address
from job.exceptions import NoInitialData
from job.forms import AddJobForm, EditJobForm, TaskForm, MilestoneForm, NoteForm
from job.models import Job, Task, Milestone, JobState, Note
from staff.models import Staff
from workflowmax.job.models import Job as WorkflowmaxJob

@login_required
def list_jobs(request):
  context_vars = dict()
  context_vars['header'] = capfirst(_('jobs'))
  try:
    staff = Staff.objects.get(user_ptr=request.user)
    context_vars['jobs'] = staff.jobs.all()
  except ObjectDoesNotExist:
    context_vars['jobs'] = Job.objects.all()
    
  return direct_to_template(request, template='job/list.html', extra_context=context_vars)

@login_required
def get_job(request, object_id):
  context_vars = dict()
  try:
    object_id = int(object_id)
  except ValueError:
    return HttpResponseRedirect(reverse('job-list'))
  job = Job.objects.get(id=object_id)
  try:
    staff = Staff.objects.get(user_ptr=request.user)
    if not job in staff.jobs.all():
      return HttpResponseRedirect(reverse('job-list'))
  except ObjectDoesNotExist:
    pass
  
  context_vars['header'] = capfirst(_('job %s') % job.name)
  context_vars['job'] = job
  return direct_to_template(request, template='job/view.html', extra_context=context_vars)

@login_required
def add_job(request):
  context_vars = dict()
  context_vars['header'] = capfirst(_('add new job'))
  job_form = AddJobForm()
  helper = FormHelper()
  submit = Submit('save',_('save'))
  helper.add_input(submit)
  layout = Layout('name', 
    'description', 
#    'state', 
    'type', 
    'start_date', 
    'due_date', 
    Row(HTML('<a href="%s">%s</a>' % (reverse('client-add'), _('add new'))), 'client'),
    Row(HTML('<a href="%s">%s</a>' % (reverse('staff-add'), _('add new'))), 'staff'),
    Row(HTML('<a href="%s">%s</a>' % (reverse('supplier-add'), _('add new'))), 'suppliers'),
    )
  helper.add_layout(layout)
  if request.method == "POST":
    job_form = AddJobForm(request.POST, request.FILES)
    if job_form.is_valid():
      job = job_form.save()
      if settings.WORKFLOWMAX_APIKEY and settings.WORKFLOWMAX_ACCOUNTKEY:
        job.wm_sync()
      job.gcal_sync()
      return HttpResponseRedirect(reverse('job-view', args=[job.id]))
  
  context_vars['form'] = job_form
  context_vars['helper'] = helper
  return direct_to_template(request, template='job/uniform.html', extra_context=context_vars)

@login_required
def edit_job(request, object_id):
  context_vars = dict()
  try:
    object_id = int(object_id)
    job = Job.objects.get(id=object_id)
  except ValueError:
    return HttpResponseRedirect(reverse('job-list'))
  except ObjectDoesNotExist:
    return HttpResponseRedirect(reverse('job-list'))

  try:
    staff = Staff.objects.get(user_ptr=request.user)
    if not job in staff.jobs.all():
      return HttpResponseRedirect(reverse('job-list'))
  except ObjectDoesNotExist:
    pass

  context_vars['header'] = capfirst(_('edit job %s') % job.name)
  job_form = EditJobForm(instance=job)
  helper = FormHelper()
  submit = Submit('save',_('save'))
  helper.add_input(submit)
  recomended_staff_html = ''
  for s in ['%s, ' % staff for staff in job.get_valid_staff()]: recomended_staff_html +=s
  layout = Layout( 
    'state', 
    Row(HTML('<span style="color:red">Recommended: %s</span>' % recomended_staff_html), HTML('<a href="%s">%s</a>' % (reverse('staff-add'), _('add new'))), 'staff'),
    Row(HTML('<a href="%s">%s</a>' % (reverse('supplier-add'), _('add new'))), 'suppliers'),
    )
  helper.add_layout(layout)

  if request.method == "POST":
    job_form = EditJobForm(request.POST, request.FILES, instance=job)
    if job_form.is_valid():
      job = job_form.save()
      if settings.WORKFLOWMAX_APIKEY and settings.WORKFLOWMAX_ACCOUNTKEY:
        job.wm_sync()
#      job.gcal_sync()
      return HttpResponseRedirect(reverse('job-view', args=[job.id]))
  
  context_vars['form'] = job_form
  context_vars['helper'] = helper
  return direct_to_template(request, template='job/uniform.html', extra_context=context_vars)

@login_required
def delete_job(request, object_id):
  context_vars = dict()
  try:
    object_id = int(object_id)
    job = Job.objects.get(id=object_id)
  except ValueError:
    return HttpResponseRedirect(reverse('job-list'))
  except ObjectDoesNotExist:
    return HttpResponseRedirect(reverse('job-list'))

  try:
    staff = Staff.objects.get(user_ptr=request.user)
    if not job in staff.jobs.all():
      return HttpResponseRedirect(reverse('job-list'))
  except ObjectDoesNotExist:
    pass

  if request.method == 'POST' and settings.WORKFLOWMAX_APIKEY and settings.WORKFLOWMAX_ACCOUNTKEY:
    job.wm_delete()
  
  return delete_object(request, object_id=job.id, model=Job, login_required=True, template_name='job/delete.html', post_delete_redirect=reverse('job-list'), extra_context={'header': capfirst(_('delete job')), 'comment': capfirst(_('you are trying to delete job "%s". Sure?') % job.name)})

@login_required
def import_jobs(request):
  context_vars = dict()
  context_vars['header'] = capfirst(_('import jobs from workflowmax'))
  context_vars['comment'] = capfirst(_('this will destroy all your local jobs, please confirm your decision.'))
  if request.method == "POST":
    try:
      for job in Job.objects.all():
        job.delete()
      wm_jobs = WorkflowmaxJob.objects.all(datetime.now() - timedelta(days=365), datetime.now() + timedelta(days=365))
  #    wm_jobs = WorkflowmaxJob.objects.current()
      for wm_job in wm_jobs:
        job = Job()
        job.wm_import(wm_job)
      return HttpResponseRedirect(reverse('job-list'))
    except NoInitialData, e:
      context_vars['error'] = capfirst(e)
  
  return direct_to_template(request, template='job/import.html', extra_context=context_vars)
  
@login_required
def add_task(request, object_id):
  context_vars = dict()
  try:
    object_id = int(object_id)
    job = Job.objects.get(id=object_id)
  except ValueError:
    return HttpResponseRedirect(reverse('job-list'))
  except ObjectDoesNotExist:
    return HttpResponseRedirect(reverse('job-list'))

  form = TaskForm()
  helper = FormHelper()
  submit = Submit('save',_('save'))
  helper.add_input(submit)
  
  if request.method == "POST":
    form = TaskForm(request.POST, request.FILES)
    if form.is_valid():
      task = form.save(commit=False)
      task.job = job
      task.save()
      form.save_m2m()
#      if settings.WORKFLOWMAX_APIKEY and settings.WORKFLOWMAX_ACCOUNTKEY:
#        task.wm_sync()
      return HttpResponseRedirect(reverse('job-view', args=[job.id]))
  
  context_vars['form'] = form
  context_vars['helper'] = helper
  return direct_to_template(request, template='job/uniform.html', extra_context=context_vars)  

@login_required
def edit_task(request, owner_id, object_id):
  context_vars = dict()
  try:
    owner_id = int(owner_id)
    job = Job.objects.get(id=owner_id)
  except ValueError:
    return HttpResponseRedirect(reverse('job-list'))
  except ObjectDoesNotExist:
    return HttpResponseRedirect(reverse('job-list'))
  try:
    object_id = int(object_id)
    task = Task.objects.get(id=object_id)
  except ValueError:
    return HttpResponseRedirect(reverse('job-view', args=[job.id]))
  except ObjectDoesNotExist:
    return HttpResponseRedirect(reverse('job-view', args=[job.id]))

  form = TaskForm(instance=task)
  helper = FormHelper()
  submit = Submit('save',_('save'))
  helper.add_input(submit)
  
  if request.method == "POST":
    form = TaskForm(request.POST, request.FILES, instance=task)
    if form.is_valid():
      form.save()
      if settings.WORKFLOWMAX_APIKEY and settings.WORKFLOWMAX_ACCOUNTKEY:
        task.wm_sync()
      return HttpResponseRedirect(reverse('job-view', args=[job.id]))
  
  context_vars['form'] = form
  context_vars['helper'] = helper
  return direct_to_template(request, template='job/uniform.html', extra_context=context_vars)

@login_required
def delete_task(request, owner_id, object_id):
  context_vars = dict()
  try:
    owner_id = int(owner_id)
    job = Job.objects.get(id=owner_id)
  except ValueError:
    return HttpResponseRedirect(reverse('job-list'))
  except ObjectDoesNotExist:
    return HttpResponseRedirect(reverse('job-list'))
  try:
    object_id = int(object_id)
    task = Task.objects.get(id=object_id)
  except ValueError, ObjectDoesNotExist:
    return HttpResponseRedirect(reverse('job-view', args=[job.id]))

#  if request.method == 'POST' and settings.WORKFLOWMAX_APIKEY and settings.WORKFLOWMAX_ACCOUNTKEY:
#    task.wm_delete()
  
  return delete_object(request, object_id=task.id, model=Task, login_required=True, template_name='job/delete.html', post_delete_redirect=reverse('job-list'), extra_context={'header': capfirst(_('delete task')), 'comment': capfirst(_('you are trying to delete task "%s". Sure?') % task.name)})


@login_required
def add_milestone(request, object_id):
  context_vars = dict()
  try:
    object_id = int(object_id)
    job = Job.objects.get(id=object_id)
  except ValueError:
    return HttpResponseRedirect(reverse('job-list'))
  except ObjectDoesNotExist:
    return HttpResponseRedirect(reverse('job-list'))

  form = MilestoneForm()
  helper = FormHelper()
  submit = Submit('save',_('save'))
  helper.add_input(submit)
  
  if request.method == "POST":
    form = MilestoneForm(request.POST, request.FILES)
    if form.is_valid():
      milestone = form.save(commit=False)
      milestone.job = job
      milestone.save()
#      if settings.WORKFLOWMAX_APIKEY and settings.WORKFLOWMAX_ACCOUNTKEY:
#        milestone.wm_sync()
      return HttpResponseRedirect(reverse('job-view', args=[job.id]))
  
  context_vars['form'] = form
  context_vars['helper'] = helper
  return direct_to_template(request, template='job/uniform.html', extra_context=context_vars)  

@login_required
def edit_milestone(request, owner_id, object_id):
  context_vars = dict()
  try:
    owner_id = int(owner_id)
    job = Job.objects.get(id=owner_id)
  except ValueError:
    return HttpResponseRedirect(reverse('job-list'))
  except ObjectDoesNotExist:
    return HttpResponseRedirect(reverse('job-list'))
  try:
    object_id = int(object_id)
    milestone = Milestone.objects.get(id=object_id)
  except ValueError, ObjectDoesNotExist:
    return HttpResponseRedirect(reverse('job-view', args=[job.id]))

  form = MilestoneForm(instance=milestone)
  helper = FormHelper()
  submit = Submit('save',_('save'))
  helper.add_input(submit)
  
  if request.method == "POST":
    form = MilestoneForm(request.POST, request.FILES, instance=milestone)
    if form.is_valid():
      form.save()
#      if settings.WORKFLOWMAX_APIKEY and settings.WORKFLOWMAX_ACCOUNTKEY:
#        milestone.wm_sync()
      return HttpResponseRedirect(reverse('job-view', args=[job.id]))
  
  context_vars['form'] = form
  context_vars['helper'] = helper
  return direct_to_template(request, template='job/uniform.html', extra_context=context_vars)

@login_required
def delete_milestone(request, owner_id, object_id):
  try:
    owner_id = int(owner_id)
    job = Job.objects.get(id=owner_id)
  except ValueError:
    return HttpResponseRedirect(reverse('job-list'))
  except ObjectDoesNotExist:
    return HttpResponseRedirect(reverse('job-list'))
  try:
    object_id = int(object_id)
    milestone = Milestone.objects.get(id=object_id)
  except ValueError:
    return HttpResponseRedirect(reverse('job-view', args=[job.id]))
  except ObjectDoesNotExist:
    return HttpResponseRedirect(reverse('job-view', args=[job.id]))

#  if request.method == 'POST' and settings.WORKFLOWMAX_APIKEY and settings.WORKFLOWMAX_ACCOUNTKEY:
#    milestone.wm_delete()
  
  return delete_object(request, object_id=milestone.id, model=Milestone, login_required=True, template_name='job/delete.html', post_delete_redirect=reverse('job-list'), extra_context={'header': capfirst(_('delete milestone')), 'comment': capfirst(_('you are trying to delete milestone "%s". Sure?') % milestone)})


@login_required
def add_note(request, object_id):
  context_vars = dict()
  try:
    object_id = int(object_id)
    job = Job.objects.get(id=object_id)
  except ValueError:
    return HttpResponseRedirect(reverse('job-list'))
  except ObjectDoesNotExist:
    return HttpResponseRedirect(reverse('job-list'))

  form = NoteForm()
  helper = FormHelper()
  submit = Submit('save',_('save'))
  helper.add_input(submit)
  
  if request.method == "POST":
    form = NoteForm(request.POST, request.FILES)
    if form.is_valid():
      note = form.save(commit=False)
      note.job = job
      note.save()
      if settings.WORKFLOWMAX_APIKEY and settings.WORKFLOWMAX_ACCOUNTKEY:
        note.wm_sync()
      return HttpResponseRedirect(reverse('job-view', args=[job.id]))
  
  context_vars['form'] = form
  context_vars['helper'] = helper
  return direct_to_template(request, template='job/uniform.html', extra_context=context_vars)  

@login_required
def edit_note(request, owner_id, object_id):
  context_vars = dict()
  try:
    owner_id = int(owner_id)
    job = Job.objects.get(id=owner_id)
  except ValueError:
    return HttpResponseRedirect(reverse('job-list'))
  except ObjectDoesNotExist:
    return HttpResponseRedirect(reverse('job-list'))
  try:
    object_id = int(object_id)
    note = Note.objects.get(id=object_id)
  except ValueError:
    return HttpResponseRedirect(reverse('job-view', args=[job.id]))
  except ObjectDoesNotExist:
    return HttpResponseRedirect(reverse('job-view', args=[job.id]))

  form = NoteForm(instance=note)
  helper = FormHelper()
  submit = Submit('save',_('save'))
  helper.add_input(submit)
  
  if request.method == "POST":
    form = NoteForm(request.POST, request.FILES, instance=note)
    if form.is_valid():
      form.save()
#      if settings.WORKFLOWMAX_APIKEY and settings.WORKFLOWMAX_ACCOUNTKEY:
#        note.wm_sync()
      return HttpResponseRedirect(reverse('job-view', args=[job.id]))
  
  context_vars['form'] = form
  context_vars['helper'] = helper
  return direct_to_template(request, template='job/uniform.html', extra_context=context_vars)

@login_required
def delete_note(request, owner_id, object_id):
  try:
    owner_id = int(owner_id)
    job = Job.objects.get(id=owner_id)
  except ValueError:
    return HttpResponseRedirect(reverse('job-list'))
  except ObjectDoesNotExist:
    return HttpResponseRedirect(reverse('job-list'))
  try:
    object_id = int(object_id)
    note = Note.objects.get(id=object_id)
  except ValueError:
    return HttpResponseRedirect(reverse('job-view', args=[job.id]))
  except ObjectDoesNotExist:
    return HttpResponseRedirect(reverse('job-view', args=[job.id]))

#  if request.method == 'POST' and settings.WORKFLOWMAX_APIKEY and settings.WORKFLOWMAX_ACCOUNTKEY:
#    note.wm_delete()
  
  return delete_object(request, object_id=note.id, model=Note, login_required=True, template_name='job/delete.html', post_delete_redirect=reverse('job-list'), extra_context={'header': capfirst(_('delete note')), 'comment': capfirst(_('you are trying to delete note "%s". Sure?') % note)})
