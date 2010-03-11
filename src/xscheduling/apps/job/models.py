from datetime import datetime, timedelta
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.translation import ugettext_lazy as _
from client.models import WorkflowmaxBase, Client
from staff.models import Staff
from supplier.models import Supplier
from workflowmax.client.models import Client as WorkflowmaxClient
from workflowmax.exceptions import ResponseStatusError
from workflowmax.job.models import Job as WorkflowmaxJob
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

class Task(WorkflowmaxBase):
#  id = xml_models.IntField(xpath="/task/id")
#  name = xml_models.CharField(xpath="/task/name")
#  description = xml_models.CharField(xpath="/task/description")
#  estimated_minutes = xml_models.IntField(xpath="/task/estimatedminutes")
#  actual_minutes = xml_models.IntField(xpath="/task/actualminutes")
#  completed = xml_models.BoolField(xpath="/task/completed")
#  billable = xml_models.BoolField(xpath="/task/billable")
#  start_date = xml_models.DateField(xpath="/task/startdate")
#  due_date = xml_models.DateField(xpath="/task/duedate")
#  assigned = xml_models.CollectionField(XmlStaff, order_by="name", xpath="/task/assigned/staff")
  name = models.CharField(_('name'), max_length=255)
  description = models.TextField(_('description'))
  estimated_minutes = models.PositiveIntegerField(_('estimated minutes'), default=0)
  actual_minutes = models.PositiveIntegerField(_('actual minutes'), default=0)
  completed = models.BooleanField(_('completed'), default=False)
  billable = models.BooleanField(_('billable'), default=True)
  start_date = models.DateTimeField(_('start date'), default=datetime.now())
  due_date = models.DateTimeField(_('due date'), default=datetime.now()+timedelta(days=1))
  staff = models.ManyToManyField(Staff, verbose_name = _('staff'), related_name='tasks')
  job = models.ForeignKey('Job', verbose_name = _('job'), related_name='tasks')

  class Meta:
    ordering = ['start_date']
    verbose_name = _('task')
    verbose_name_plural = _('tasks')

  def __unicode__(self):
    return self.name

class Milestone(models.Model):
#  date = xml_models.DateField(xpath="/milestone/date")
#  description = xml_models.CharField(xpath="/milestone/description")
#  completed = xml_models.BoolField(xpath="/milestone/completed")
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


class Job(WorkflowmaxBase):
#  id = xml_models.CharField(xpath="/job/id")
#  name = xml_models.CharField(xpath="/job/name")
#  description = xml_models.CharField(xpath="/job/description")
#  state = xml_models.CharField(xpath="/job/state")
#  type = xml_models.CharField(xpath="/job/type")
#  start_date = xml_models.DateField(xpath="/job/startdate")
#  due_date = xml_models.DateField(xpath="/job/duedate")
#  clients = xml_models.CollectionField(XmlClient, order_by="name", xpath="/job/client")
#  contacts = xml_models.CollectionField(XmlContact, order_by="name", xpath="/job/contact")
#  assigned = xml_models.CollectionField(XmlStaff, order_by="name", xpath="/job/assigned/staff")
#  tasks = xml_models.CollectionField(XmlTask, order_by="id", xpath="/job/tasks/task")
#  milestones = xml_models.CollectionField(XmlMilestone, order_by="date", xpath="/job/milestones/milestone")
#  notes = xml_models.Collection(XmlNote, order_by="title", xpath="/job/notes/note")
  name = models.CharField(_('name'), max_length=255)
  description = models.TextField(_('description'))
  state = models.ForeignKey(JobState, verbose_name = _('state'), related_name='jobs')
  type = models.ForeignKey(JobType, verbose_name = _('type'), related_name='jobs')
  start_date = models.DateTimeField(_('start date'), default=datetime.now())
  due_date = models.DateTimeField(_('due date'), default=datetime.now()+timedelta(days=1))
  client = models.ForeignKey(Client, verbose_name = _('client'), related_name='jobs')
  staff = models.ManyToManyField(Staff, verbose_name = _('staff'), related_name='jobs')
  suppliers = models.ManyToManyField(Supplier, verbose_name = _('suppliers'), related_name='jobs')

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
      # we MUST have at least one state in db
      self.state = JobState.objects.all()[0]
    if wm_object.type:
      self.type, is_new = JobType.objects.get_or_create(name=wm_object.type)
    else:
      # we MUST have at least one type in db
      self.type = JobType.objects.all()[0]
    for wm_client in wm_object.clients:
      self.client, is_new = Client.objects.get_or_create(wm_id=wm_client.id, name=wm_client.name)
    self.save()
    for wm_staff in wm_object.assigned:
      staff, is_new = Staff.objects.get_or_create(wm_id=wm_staff.id, name=wm_staff.name)
      self.staff.add(staff)

  def wm_delete(self):
    if self.wm_id:
      wm_job = WorkflowmaxJob.objects.get(id=self.wm_id)
      wm_job.delete()

  def wm_sync(self):
    if self.name and self.description and self.start_date and self.due_date and self.client and self.client.wm_id:
      wm_job = WorkflowmaxJob()
      if self.wm_id:
        wm_job.id = self.wm_id
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

