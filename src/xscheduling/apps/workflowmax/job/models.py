from django.db import models
import xml_models
import rest_client
from BeautifulSoup import BeautifulStoneSoup, BeautifulSoup, Tag, NavigableString
from django.conf import settings
from workflowmax.exceptions import ResponseStatusError, InvalidObjectType

from workflowmax.client.models import XmlNote

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

class Note(object):
  post = "http://api.workflowmax.com/job.api/note?apiKey=%s&accountKey=%s" % (settings.WORKFLOWMAX_APIKEY, settings.WORKFLOWMAX_ACCOUNTKEY)

  def __init__(self, xml_note=None, xml=None):
    if xml_note and not isinstance(xml_note, xml_models.Model):
      raise InvalidObjectType('object is not child of xml_models.Model')
    self.xml_note = xml_note
    if xml:
      self.xml_note = XmlNote(xml=xml)

  def __getattr__(self, name):
    return getattr(self.xml_note, name)

  def save(self):
    soup = BeautifulSoup()
    root_tag = Tag(soup, 'Note')
    soup.insert(0, root_tag)
    i = 0

    try:
      job_tag = Tag(soup, 'Job')
      job_tag.insert(0, NavigableString('%s' % self.owner_id))
      root_tag.insert(i, job_tag)
      i = i+1
    except AttributeError:
      raise ValueError("You must provide job id.")  
    
    try:
      title_tag = Tag(soup, 'Title')
      title_tag.insert(0, NavigableString(self.title))
      root_tag.insert(i, title_tag)
      i = i+1
    except AttributeError:
      raise ValueError("You must provide note's title.")
    
    try:
      text_tag = Tag(soup, 'Text')
      text_tag.insert(0, NavigableString(self.text))
      root_tag.insert(i, text_tag)
      i = i+1
    except AttributeError:
      raise ValueError("You must provide note's text.")
    
    try:
      if self.folder:
        folder_tag = Tag(soup, 'Folder')
        folder_tag.insert(0, NavigableString(self.folder))
        root_tag.insert(i, folder_tag)
        i = i+1
    except AttributeError:
      pass
    
    try:
      if self.public:
        public_tag = Tag(soup, 'Public')
        public_tag.insert(0, NavigableString(str(self.public).lower()))
        root_tag.insert(i, public_tag)
        i = i+1
    except AttributeError:
      pass
    
    response = rest_client.Client("").POST(self.post, str(soup))
    return Note(xml=response.content)

  def to_dict(self):
    d = dict()
    d['title'] = self.title
    d['text'] = self.text
    d['folder'] = self.folder
    d['public'] = self.public
    return d

class XmlJobManager(object):
  current_url = "http://api.workflowmax.com/job.api/current?detailed=%s&apiKey=%s&accountKey=%s" % ('%s', settings.WORKFLOWMAX_APIKEY, settings.WORKFLOWMAX_ACCOUNTKEY)
  list_url = "http://api.workflowmax.com/job.api/list?from=%s&to=%s&detailed=%s&apiKey=%s&accountKey=%s" % ('%s', '%s', '%s', settings.WORKFLOWMAX_APIKEY, settings.WORKFLOWMAX_ACCOUNTKEY)
  staff_url = "http://api.workflowmax.com/job.api/staff/%s?apiKey=%s&accountKey=%s" % ('%s', settings.WORKFLOWMAX_APIKEY, settings.WORKFLOWMAX_ACCOUNTKEY)

  def _handle_response(self, response):
    soup = BeautifulStoneSoup(response.content)
    if soup.status and soup.status.contents[0].lower() == 'error':
      raise ResponseStatusError(soup.errordescription.contents[0])
    objects = list()
    for object_xml in soup.jobs.contents:
      objects.append(XmlJob(xml=str(object_xml)))
    return objects
  
  def current(self, detailed=True):
    response = rest_client.Client("").GET(self.current_url % str(detailed).lower())
    return self._handle_response(response)

  def all(self, from_date, to_date, detailed=True):
    response = rest_client.Client("").GET(self.list_url % (from_date, to_date, str(detailed).lower()))
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
    xml_objects = XmlJob.job_objects.all(from_date.strftime('%Y%m%d'), to_date.strftime('%Y%m%d'))
    return self._handle_xml_objects(xml_objects)

  def get(self, **kw):
    return Job(XmlJob.objects.get(**kw))

  def filter(self, **kw):
    if kw['staff']:
      return self._handle_xml_objects(XmlJob.job_objects.filter(staff=kw['staff']))
    return []

class Job(object):
  objects = JobManager()
  put_state = "http://api.workflowmax.com/job.api/state?apiKey=%s&accountKey=%s" % (settings.WORKFLOWMAX_APIKEY, settings.WORKFLOWMAX_ACCOUNTKEY)
  put_assign = "http://api.workflowmax.com/job.api/assign?apiKey=%s&accountKey=%s" % (settings.WORKFLOWMAX_APIKEY, settings.WORKFLOWMAX_ACCOUNTKEY)
  post = "http://api.workflowmax.com/job.api/add?apiKey=%s&accountKey=%s" % (settings.WORKFLOWMAX_APIKEY, settings.WORKFLOWMAX_ACCOUNTKEY)
  delete_url = "http://api.workflowmax.com/job.api/delete?apiKey=%s&accountKey=%s" % (settings.WORKFLOWMAX_APIKEY, settings.WORKFLOWMAX_ACCOUNTKEY)

  def __init__(self, xml_object=None, xml=None):
    self.xml_object = xml_object
    if xml_object and not isinstance(xml_object, xml_models.Model):
      raise InvalidObjectType('object is not child of xml_models.Model')
    if xml:
      self.xml_object = XmlJob(xml=xml)

  def __getattr__(self, name):
    return getattr(self.xml_object, name)

  def _prepare_soup_root_tag(self):
    soup = BeautifulSoup()
    root_tag = Tag(soup, 'Job')
    soup.insert(0, root_tag)
    return (soup, root_tag)

  def _prepare_soup_put_state(self):
    soup, root_tag = self._prepare_soup_root_tag()
    i = 0
    try:
      id_tag = Tag(soup, 'ID')
      id_tag.insert(0, NavigableString(self.id))
      root_tag.insert(i, id_tag)
      i = i+1
    except AttributeError:
      raise ValueError("You must have ID for PUT.")
    
    try:
      state_tag = Tag(soup, 'State')
      state_tag.insert(0, NavigableString(self.state))
      root_tag.insert(i, state_tag)
      i = i+1
    except AttributeError:
      raise ValueError("You must provide job state.")
    return soup

  def _prepare_soup_put_assign(self):
    soup, root_tag = self._prepare_soup_root_tag()
    try:
      id_tag = Tag(soup, 'ID')
      id_tag.insert(0, NavigableString(self.id))
      root_tag.insert(0, id_tag)
    except AttributeError:
      raise ValueError("You must have ID for PUT.")
    
    i = 1
    old_list = [x.id for x in self.xml_object.assigned]
    new_list = [x.id for x in self.assigned]
    added = [x for x in new_list if x not in old_list]
    removed = [x for x in old_list if x not in new_list]
    for staff_id in added:
      add_tag = Tag(soup, 'add', [('id', '%s' % staff_id),])
      add_tag.isSelfClosing=True
      root_tag.insert(i, add_tag)
      i = i+1
    for staff_id in removed:
      remove_tag = Tag(soup, 'remove', [('id', '%s' % staff_id),])
      remove_tag.isSelfClosing=True
      root_tag.insert(i, remove_tag)
      i = i+1
    return soup

  def _prepare_soup_post(self):
    soup, root_tag = self._prepare_soup_root_tag()
    i = 0
    try:
      name_tag = Tag(soup, 'Name')
      name_tag.insert(0, NavigableString(self.name))
      root_tag.insert(i, name_tag)
      i = i+1
    except AttributeError:
      raise ValueError("You must provide job name.")  

    try:
      description_tag = Tag(soup, 'Description')
      description_tag.insert(0, NavigableString(self.description))
      root_tag.insert(i, description_tag)
      i = i+1
    except AttributeError:
      raise ValueError("You must provide job description.")  

    try:
      client_id_tag = Tag(soup, 'ClientID')
      client_id_tag.insert(0, NavigableString('%d' % self.clients[0].id))
      root_tag.insert(i, client_id_tag)
      i = i+1
    except AttributeError:
      raise ValueError("You must provide job client id.")  
    
    try:
      start_date_tag = Tag(soup, 'StartDate')
      start_date_tag.insert(0, NavigableString(self.start_date.strftime('%Y%m%d')))
      root_tag.insert(i, start_date_tag)
      i = i+1
    except AttributeError:
      raise ValueError("You must provide job start date.")  

    try:
      due_date_tag = Tag(soup, 'DueDate')
      due_date_tag.insert(0, NavigableString(self.due_date.strftime('%Y%m%d')))
      root_tag.insert(i, due_date_tag)
      i = i+1
    except AttributeError:
      raise ValueError("You must provide job due date.")  

    try:
      if self.contacts:
        contact_id_tag = Tag(soup, 'ClientID')
        contact_id_tag.insert(0, NavigableString('%d' % self.contacts[0].id))
        root_tag.insert(i, contact_id_tag)
        i = i+1
    except AttributeError:
      pass
    
    try:
      if self.client_number:
        client_number_tag = Tag(soup, 'ClientNumber')
        client_number_tag.insert(0, NavigableString(self.client_number))
        root_tag.insert(i, client_number_tag)
        i = i+1
    except AttributeError:
      pass
    
    try:
      if self.template_id:
        template_id_tag = Tag(soup, 'TemplateID')
        template_id_tag.insert(0, NavigableString(self.template_id))
        root_tag.insert(i, template_id_tag)
        i = i+1
    except AttributeError:
      pass    
    return soup

  def save(self):
    method = 'POST'
    try:
      self.id
      method = 'PUT'
    except AttributeError:
      pass

    if method == 'PUT':
      if self.state != self.xml_object.state:
        soup = self._prepare_soup_put_state()
        response = rest_client.Client("").PUT(self.put_state, str(soup))
        Job(xml=response.content) # exception will be raised in case of error
      soup = self._prepare_soup_put_assign()
      response = rest_client.Client("").PUT(self.put_assign, str(soup))
    else:
      soup = self._prepare_soup_post()
      response = rest_client.Client("").POST(self.post, str(soup))
    return Job(xml=response.content)

  def delete(self):
    soup = BeautifulSoup()
    job_tag = Tag(soup, 'Job')
    soup.insert(0, job_tag)
    try:
      id_tag = Tag(soup, 'ID')
      id_tag.insert(0, NavigableString(self.id))
      job_tag.insert(0, id_tag)
    except AttributeError:
      raise ValueError("You must have id for delete operation.")  

    response = rest_client.Client("").POST(self.delete_url, str(soup))
    soup = BeautifulStoneSoup(response.content)
    if soup.status and soup.status.contents[0].lower() == 'error':
      raise ResponseStatusError(soup.errordescription.contents[0])
    
  def to_dict(self):
    d = dict()
    d['state'] = self.state
    d['assigned'] = [x.id for x in self.assigned]
#    d['name'] = self.name
#    d['description'] = self.description
#    d['start_date'] = self.start_date
#    d['due_date'] = self.due_date
#    d['client_id'] = self.clients[0].id
#    d['contact_id'] = self.contacts[0].id if self.contacts
#    d['client_number'] = self.client_number if hasattr(self, 'client_number')
    return d

