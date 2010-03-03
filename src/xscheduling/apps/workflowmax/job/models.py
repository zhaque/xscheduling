from django.db import models
import xml_models
import rest_client
from BeautifulSoup import BeautifulStoneSoup, BeautifulSoup, Tag, NavigableString
from django.conf import settings
from workflowmax.exceptions import ResponseStatusError, InvalidObjectType

from workflowmax.client.models import Note as XmlNote

class XmlContact(xml_models.Model):
  id = xml_models.IntField(xpath="/contact/id")
  name = xml_models.CharField(xpath="/contact/name")
  
class XmlClient(xml_models.Model):
  id = xml_models.IntField(xpath="/client/id")
  name = xml_models.CharField(xpath="/client/name")

class XmlStaff(xml_models.Model):
  id = xml_models.IntField(xpath="/staff/id")
  name = xml_models.CharField(xpath="/staff/name")

class XmlTask(xml_models.Model):
  id = xml_models.IntField(xpath="/task/id")
  name = xml_models.CharField(xpath="/task/name")
  description = xml_models.CharField(xpath="/task/description")
  estimated_minutes = xml_models.IntField(xpath="/task/estimatedminutes")
  actual_minutes = xml_models.IntField(xpath="/task/actualminutes")
  completed = xml_models.BoolField(xpath="/task/completed")
  billable = xml_models.BoolField(xpath="/task/billable")
  start_date = xml_models.DateField(xpath="/task/startdate")
  due_date = xml_models.DateField(xpath="/task/duedate")
  assigned = xml_models.CollectionField(XmlStaff, order_by="name", xpath="/task/assigned/staff")

class XmlMilestone(xml_models.Model):
  date = xml_models.DateField(xpath="/milestone/date")
  description = xml_models.CharField(xpath="/milestone/description")
  completed = xml_models.BoolField(xpath="/milestone/completed")


class XmlJobManager(object):
  current_url = "http://api.workflowmax.com/job.api/current?detailed=%s&apiKey=%s&accountKey=%s" % ('%s', settings.WORKFLOWMAX_APIKEY, settings.WORKFLOWMAX_ACCOUNTKEY)
  list_url = "http://api.workflowmax.com/job.api/list?from=%s&to=%s&apiKey=%s&accountKey=%s" % ('%s', '%s', settings.WORKFLOWMAX_APIKEY, settings.WORKFLOWMAX_ACCOUNTKEY)
  staff_url = "http://api.workflowmax.com/job.api/staff/%s?apiKey=%s&accountKey=%s" % ('%s', settings.WORKFLOWMAX_APIKEY, settings.WORKFLOWMAX_ACCOUNTKEY)

  def _handle_response(self, response):
    soup = BeautifulStoneSoup(response.content)
    if soup.status and soup.status.contents[0].lower() == 'error':
      raise ResponseStatusError(soup.errordescription.contents[0])
    objects = list()
    for object_xml in soup.jobs.contents:
      objects.append(XmlJob(xml=str(object_xml)))
    return objects
  
  def current(self, detailed=False):
    response = rest_client.Client("").GET(self.current_url % str(detailed).lower())
    return self._handle_response(response)

  def all(self, from_date, to_date):
    response = rest_client.Client("").GET(self.list_url % (from_date, to_date))
    return self._handle_response(response)

  def filter(self, staff):
    response = rest_client.Client("").GET(self.staff_url % staff.id)
    return self._handle_response(response)

class XmlJob(xml_models.Model):
  id = xml_models.CharField(xpath="/job/id")
  name = xml_models.CharField(xpath="/job/name")
  description = xml_models.CharField(xpath="/job/description")
  state = xml_models.CharField(xpath="/job/state")
  type = xml_models.CharField(xpath="/job/type")
  start_date = xml_models.DateField(xpath="/job/startdate")
  due_date = xml_models.DateField(xpath="/job/duedate")
  clients = xml_models.CollectionField(XmlClient, order_by="name", xpath="/job/client")
  contacts = xml_models.CollectionField(XmlContact, order_by="name", xpath="/job/contact")
  assigned = xml_models.CollectionField(XmlStaff, order_by="name", xpath="/job/assigned/staff")
  tasks = xml_models.CollectionField(XmlTask, order_by="id", xpath="/job/tasks/task")
  milestones = xml_models.CollectionField(XmlMilestone, order_by="date", xpath="/job/milestones/milestone")
  notes = xml_models.Collection(XmlNote, order_by="title", xpath="/job/notes/note")

  finders = { (id,): "http://api.workflowmax.com/job.api/get/%s?apiKey=%s&accountKey=%s" % ('%s', settings.WORKFLOWMAX_APIKEY, settings.WORKFLOWMAX_ACCOUNTKEY)}
  
  job_objects = XmlJobManager()

  def validate_on_load(self):
    soup = BeautifulStoneSoup(self._xml)
    if soup.status and soup.status.contents[0].lower() == 'error':
      raise ResponseStatusError(soup.errordescription.contents[0])
    self._xml = str(soup.job)

class JobManager(object):
  def _handle_xml_objects(self, xml_objects):
    res = list()
    for xml_object in xml_objects:
      res.append(Job(xml_object))
    return res

  def current(self, detailed=False):
    xml_objects = XmlJob.job_objects.current(detailed)
    return self._handle_xml_objects(xml_objects)

  def all(self, from_date, to_date):
    xml_objects = XmlJob.job_objects.all(from_date, to_date)
    return self._handle_xml_objects(xml_objects)

  def get(self, **kw):
    return Job(XmlJob.objects.get(**kw))

  def filter(self, **kw):
    if kw['staff']:
      return self._handle_xml_objects(XmlJob.job_objects.filter(staff=kw['staff']))
    return []

class Job(object):
  objects = JobManager()
  put = "http://api.workflowmax.com/job.api/state?apiKey=%s&accountKey=%s" % (settings.WORKFLOWMAX_APIKEY, settings.WORKFLOWMAX_ACCOUNTKEY)
  post = "http://api.workflowmax.com/job.api/add?apiKey=%s&accountKey=%s" % (settings.WORKFLOWMAX_APIKEY, settings.WORKFLOWMAX_ACCOUNTKEY)

  def __init__(self, xml_object=None, xml=None):
    self.xml_object = xml_object
    if xml_object and not isinstance(xml_object, xml_models.Model):
      raise InvalidObjectType('object is not child of xml_models.Model')
    if xml:
      self.xml_object = XmlJob(xml=xml)

  def __getattr__(self, name):
    return getattr(self.xml_object, name)

  def save(self):
    soup = BeautifulSoup()
    job_tag = Tag(soup, 'Job')
    soup.insert(0, job_tag)
    i = 0
    method = 'POST'
    try:
      id_tag = Tag(soup, 'ID')
      id_tag.insert(0, NavigableString(self.id))
      job_tag.insert(i, id_tag)
      i = i+1
      method = 'PUT'
    except AttributeError:
      pass
    
    if method == 'PUT':
      try:
        state_tag = Tag(soup, 'State')
        state_tag.insert(0, NavigableString(self.name))
        job_tag.insert(i, state_tag)
        i = i+1
      except AttributeError:
        raise ValueError("You must provide job state.")
    else:
      try:
        name_tag = Tag(soup, 'Name')
        name_tag.insert(0, NavigableString(self.name))
        job_tag.insert(i, name_tag)
        i = i+1
      except AttributeError:
        raise ValueError("You must provide job name.")  
  
      try:
        description_tag = Tag(soup, 'Description')
        description_tag.insert(0, NavigableString(self.description))
        job_tag.insert(i, description_tag)
        i = i+1
      except AttributeError:
        raise ValueError("You must provide job description.")  
  
      try:
        client_id_tag = Tag(soup, 'ClientID')
        client_id_tag.insert(0, NavigableString('%d' % self.clients[0].id))
        job_tag.insert(i, client_id_tag)
        i = i+1
      except AttributeError:
        raise ValueError("You must provide job client id.")  
      
      try:
        start_date_tag = Tag(soup, 'StartDate')
        start_date_tag.insert(0, NavigableString(self.start_date.strftime('%Y%m%d')))
        job_tag.insert(i, start_date_tag)
        i = i+1
      except AttributeError:
        raise ValueError("You must provide job start date.")  
  
      try:
        due_date_tag = Tag(soup, 'DueDate')
        due_date_tag.insert(0, NavigableString(self.due_date.strftime('%Y%m%d')))
        job_tag.insert(i, due_date_tag)
        i = i+1
      except AttributeError:
        raise ValueError("You must provide job due date.")  
  
      try:
        if self.contacts:
          contact_id_tag = Tag(soup, 'ClientID')
          contact_id_tag.insert(0, NavigableString('%d' % self.contacts[0].id))
          job_tag.insert(i, contact_id_tag)
          i = i+1
      except AttributeError:
        pass
      
      try:
        if self.client_number:
          client_number_tag = Tag(soup, 'ClientNumber')
          client_number_tag.insert(0, NavigableString(self.client_number))
          job_tag.insert(i, client_number_tag)
          i = i+1
      except AttributeError:
        pass
      
      try:
        if self.template_id:
          template_id_tag = Tag(soup, 'TemplateID')
          template_id_tag.insert(0, NavigableString(self.template_id))
          job_tag.insert(i, template_id_tag)
          i = i+1
      except AttributeError:
        pass    

    if method == "PUT":
      response = rest_client.Client("").PUT(self.put, str(soup))
    else:
      response = rest_client.Client("").POST(self.post, str(soup))
    return Job(xml=response.content)

  def to_dict(self):
    d = dict()
    d['state'] = self.state
#    d['name'] = self.name
#    d['description'] = self.description
#    d['start_date'] = self.start_date
#    d['due_date'] = self.due_date
#    d['client_id'] = self.clients[0].id
#    d['contact_id'] = self.contacts[0].id if self.contacts
#    d['client_number'] = self.client_number if hasattr(self, 'client_number')
    return d

