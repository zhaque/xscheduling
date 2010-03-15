from datetime import datetime, timedelta
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.translation import ugettext_lazy as _
from client.models import WorkflowmaxBase, Client, NoteBase
from job.exceptions import NoInitialData
from staff.models import Staff
from supplier.models import Supplier
from workflowmax.client.models import Client as WorkflowmaxClient
from workflowmax.exceptions import ResponseStatusError
from workflowmax.job.models import Job as WorkflowmaxJob, Note as WorkflowmaxNote
from workflowmax.staff.models import Staff as WorkflowmaxStaff

class JobState(models.Model):
  order = models.PositiveSmallIntegerField(_('order'), default=10)
  name = models.CharField(_('name'), max_length=255)

  class Meta:
    ordering = ['order']
    verbose_name = _('state')
    verbose_name_plural = _('states')

  def __unicode__(self):
    return self.name

class JobType(models.Model):
# I think we don't need order for types, maybe we need something like short name or abbreviations. 
#  order = models.SmallPositiveIntegerField(_('order'))
  name = models.CharField(_('name'), max_length=255)

  class Meta:
    ordering = ['name']
    verbose_name = _('type')
    verbose_name_plural = _('types')

  def __unicode__(self):
    return self.name

class Note(NoteBase):
  """Job note can be added, but cannot be edited, so it does not have wm_id, ie we can use wm_sync method only to add note."""
  job = models.ForeignKey('Job', verbose_name="job", related_name='notes')

  def wm_sync(self):
    if self.title and self.job.wm_id and self.text:
      wm_note = WorkflowmaxNote()
      wm_note.owner_id = self.job.wm_id    
      wm_note.title = self.title
      wm_note.text = self.text
      wm_note.folder = self.folder
      wm_note.public = self.public
      wm_note.save()

class Task(WorkflowmaxBase):
  name = models.CharField(_('name'), max_length=255)
  description = models.TextField(_('description'), null=True, blank=True)
  estimated_minutes = models.PositiveIntegerField(_('estimated minutes'), default=0)
  actual_minutes = models.PositiveIntegerField(_('actual minutes'), default=0)
  completed = models.BooleanField(_('completed'), default=False)
  billable = models.BooleanField(_('billable'), default=True)
  start_date = models.DateTimeField(_('start date'), default=datetime.now(), null=True, blank=True)
  due_date = models.DateTimeField(_('due date'), default=datetime.now()+timedelta(days=1), null=True, blank=True)
  staff = models.ManyToManyField(Staff, verbose_name = _('staff'), related_name='tasks')
  job = models.ForeignKey('Job', verbose_name = _('job'), related_name='tasks')

  class Meta:
    ordering = ['start_date']
    verbose_name = _('task')
    verbose_name_plural = _('tasks')

  def __unicode__(self):
    return self.name

  def wm_import(self, wm_object):
    self.wm_id = wm_object.id
    self.name = wm_object.name
    self.description = wm_object.description
    self.estimated_minutes = wm_object.estimated_minutes
    self.actual_minutes = wm_object.actual_minutes
    self.completed = wm_object.completed
    self.billable = wm_object.billable
    if wm_object.start_date:
      self.start_date = wm_object.start_date
    if wm_object.due_date:
      self.due_date = wm_object.due_date
    self.save()
    for wm_staff in wm_object.assigned:
      staff, is_new = Staff.objects.get_or_create(wm_id=wm_staff.id, name=wm_staff.name)
      self.staff.add(staff)

class Milestone(models.Model):
  date = models.DateTimeField(_('date'), default=datetime.now()+timedelta(days=7))
  description = models.TextField(_('description'))
  completed = models.BooleanField(_('completed'), default=False)
  job = models.ForeignKey('Job', verbose_name = _('job'), related_name='milestones')

  class Meta:
    ordering = ['date']
    verbose_name = _('milestone')
    verbose_name_plural = _('milestones')

  def __unicode__(self):
    return self.description

  def wm_import(self, wm_object):
    self.date = wm_object.date
    self.description = wm_object.description
    self.completed = wm_object.completed

class Job(WorkflowmaxBase):
  name = models.CharField(_('name'), max_length=255)
  description = models.TextField(_('description'))
  state = models.ForeignKey(JobState, verbose_name = _('state'), related_name='jobs')
  type = models.ForeignKey(JobType, verbose_name = _('type'), related_name='jobs')
  start_date = models.DateTimeField(_('start date'), default=datetime.now())
  due_date = models.DateTimeField(_('due date'), default=datetime.now()+timedelta(days=1))
  client = models.ForeignKey(Client, verbose_name = _('client'), related_name='jobs')
  staff = models.ManyToManyField(Staff, verbose_name = _('staff'), related_name='jobs', null=True, blank=True)
  suppliers = models.ManyToManyField(Supplier, verbose_name = _('suppliers'), related_name='jobs', null=True, blank=True)

  class Meta:
    ordering = ['name']
    verbose_name = _('job')
    verbose_name_plural = _('jobs')

  def __unicode__(self):
    return self.name

  def wm_import(self, wm_object):
    self.wm_id = wm_object.id
    self.name = wm_object.name
    self.description = wm_object.description
    self.start_date = wm_object.start_date
    self.due_date = wm_object.due_date
    if wm_object.state:
      self.state, is_new = JobState.objects.get_or_create(name=wm_object.state)
    else:
      # it's impossible that wm job has no state, but if we get here we MUST have at least one state in db
      self.state = JobState.objects.all()[0]
    if wm_object.type:
      self.type, is_new = JobType.objects.get_or_create(name=wm_object.type)
    else:
      # we MUST have at least one type in db
      try:
        self.type = JobType.objects.all()[0]
      except IndexError:
        raise NoInitialData('data fixtures were not loaded')
    for wm_client in wm_object.clients:
      self.client, is_new = Client.objects.get_or_create(wm_id=wm_client.id, name=wm_client.name)
    self.save()
    for wm_staff in wm_object.assigned:
      staff, is_new = Staff.objects.get_or_create(wm_id=wm_staff.id, name=wm_staff.name)
      self.staff.add(staff)
    for wm_task in wm_object.tasks:
      task = Task()
      task.job = self
      task.wm_import(wm_task)
    for wm_milestone in wm_object.milestones:
      milestone = Milestone()
      milestone.job = self
      milestone.wm_import(wm_milestone)
      milestone.save()
    for wm_note in wm_object.notes:
      note = Note()
      note.job = self
      note.wm_import(wm_note)
      note.save()

  def wm_delete(self):
    if self.wm_id:
      wm_job = WorkflowmaxJob.objects.get(id=self.wm_id)
      wm_job.delete()

  def wm_sync(self):
    if self.name and self.description and self.start_date and self.due_date and self.client and self.client.wm_id:
      wm_job = WorkflowmaxJob()
      if self.wm_id:
        wm_job = WorkflowmaxJob.objects.get(id=self.wm_id)
#        wm_job.state = self.state.name
      wm_job.name = self.name
      wm_job.description = self.description
      wm_job.start_date = self.start_date
      wm_job.due_date = self.due_date
      wm_client = WorkflowmaxClient.objects.get(id=self.client.wm_id)
      wm_job.clients = [wm_client,]
      wm_job = wm_job.save()
      if not self.wm_id:
        self.wm_id = wm_job.id
        self.save()
      if self.staff.all():
        wm_job.assigned = []
        for staff in self.staff.all():
          try:
            wm_job.assigned.append(WorkflowmaxStaff.objects.get(id=staff.wm_id))
          except ResponseStatusError:
            pass
        wm_job.save()

