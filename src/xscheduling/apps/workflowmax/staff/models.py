from django.db import models
import xml_models
import rest_client
from BeautifulSoup import BeautifulStoneSoup, BeautifulSoup, Tag, NavigableString
from django.conf import settings
from workflowmax.exceptions import ResponseStatusError, InvalidObjectType

class XmlStaffManager(object):
  list_url = "http://api.workflowmax.com/staff.api/list?apiKey=%s&accountKey=%s" % (settings.WORKFLOWMAX_APIKEY, settings.WORKFLOWMAX_ACCOUNTKEY)

  def all(self):
    response = rest_client.Client("").GET(self.list_url) 
    soup = BeautifulStoneSoup(response.content)
    if soup.status and soup.status.contents[0].lower() == 'error':
      raise ResponseStatusError(soup.errordescription.contents[0])
    objects = list()
    for object_xml in soup.stafflist.contents:
      objects.append(XmlStaff(xml=str(object_xml)))
    return objects

class XmlStaff(xml_models.Model):
  id = xml_models.IntField(xpath="/staff/id")
  name = xml_models.CharField(xpath="/staff/name")
  address = xml_models.CharField(xpath="/staff/address")
  phone = xml_models.CharField(xpath="/staff/phone")
  mobile = xml_models.CharField(xpath="/staff/mobile")
  email = xml_models.CharField(xpath="/staff/email")
  payrollcode = xml_models.CharField(xpath="/staff/payrollcode")
  
  finders = { (id,): "http://api.workflowmax.com/staff.api/get/%s?apiKey=%s&accountKey=%s" % ('%s', settings.WORKFLOWMAX_APIKEY, settings.WORKFLOWMAX_ACCOUNTKEY)} 

  staff_objects = XmlStaffManager()

  def validate_on_load(self):
    soup = BeautifulStoneSoup(self._xml)
    if soup.status and soup.status.contents[0].lower() == 'error':
      raise ResponseStatusError(soup.errordescription.contents[0])
    self._xml = str(soup.staff)

class StaffManager(object):
  def all(self):
    xml_objects = XmlStaff.staff_objects.all()
    res = list()
    for xml_object in xml_objects:
      res.append(Staff(xml_object))
    return res

  def get(self, **kw):
    return Staff(XmlStaff.objects.get(**kw))

class Staff(object):
  objects = StaffManager()
  put = "http://api.workflowmax.com/staff.api/update?apiKey=%s&accountKey=%s" % (settings.WORKFLOWMAX_APIKEY, settings.WORKFLOWMAX_ACCOUNTKEY)
  post = "http://api.workflowmax.com/staff.api/add?apiKey=%s&accountKey=%s" % (settings.WORKFLOWMAX_APIKEY, settings.WORKFLOWMAX_ACCOUNTKEY)
  delete_url = "http://api.workflowmax.com/staff.api/delete?apiKey=%s&accountKey=%s" % (settings.WORKFLOWMAX_APIKEY, settings.WORKFLOWMAX_ACCOUNTKEY)

  def __init__(self, xml_object=None, xml=None):
    self.xml_object = xml_object
    if xml_object and not isinstance(xml_object, xml_models.Model):
      raise InvalidObjectType('object is not a child of xml_models.Model')
    if xml:
      self.xml_object = XmlStaff(xml=xml)

  def __getattr__(self, name):
    return getattr(self.xml_object, name)

  def save(self):
    soup = BeautifulSoup()
    staff_tag = Tag(soup, 'Staff')
    soup.insert(0, staff_tag)
    i = 0
    method = "POST"
    try:
      id_tag = Tag(soup, 'ID')
      id_tag.insert(0, NavigableString('%d' % self.id))
      staff_tag.insert(i, id_tag)
      i = i+1
      method = "PUT"
    except AttributeError:
      pass
    
    try:
      name_tag = Tag(soup, 'Name')
      name_tag.insert(0, NavigableString(self.name))
      staff_tag.insert(i, name_tag)
      i = i+1
    except AttributeError:
      raise ValueError("You must provide staff name.")  
    
    try:
      if self.address:
        address_tag = Tag(soup, 'Address')
        address_tag.insert(0, NavigableString(self.address))
        staff_tag.insert(i, address_tag)
        i = i+1
    except AttributeError:
      pass
    
    try:
      if self.phone:
        phone_tag = Tag(soup, 'Phone')
        phone_tag.insert(0, NavigableString(self.phone))
        staff_tag.insert(i, phone_tag)
        i = i+1
    except AttributeError:
      pass

    try:
      if self.mobile:
        mobile_tag = Tag(soup, 'Mobile')
        mobile_tag.insert(0, NavigableString(self.mobile))
        staff_tag.insert(i, mobile_tag)
        i = i+1
    except AttributeError:
      pass
    
    try:
      if self.email:
        email_tag = Tag(soup, 'Email')
        email_tag.insert(0, NavigableString(self.email))
        staff_tag.insert(i, email_tag)
        i = i+1
    except AttributeError:
      pass
    
    try:
      if self.payrollcode:
        payrollcode_tag = Tag(soup, 'PayrollCode')
        payrollcode_tag.insert(0, NavigableString(self.payrollcode))
        staff_tag.insert(i, payrollcode_tag)
        i = i+1
    except AttributeError:
      pass
    
    if method == "PUT":
      response = rest_client.Client("").PUT(self.put, str(soup))
    else:
      response = rest_client.Client("").POST(self.post, str(soup))
    return Staff(xml=response.content)

  def delete(self):
    soup = BeautifulSoup()
    staff_tag = Tag(soup, 'Staff')
    soup.insert(0, staff_tag)
    try:
      id_tag = Tag(soup, 'ID')
      id_tag.insert(0, NavigableString('%d' % self.id))
      staff_tag.insert(0, id_tag)
    except AttributeError:
      raise ValueError("You must have id for delete operation.")  

    response = rest_client.Client("").POST(self.delete_url, str(soup))
    soup = BeautifulStoneSoup(response.content)
    if soup.status and soup.status.contents[0].lower() == 'error':
      raise ResponseStatusError(soup.errordescription.contents[0])
    
  def to_dict(self):
    d = dict()
    d['name'] = self.name
    d['address'] = self.address
    d['phone'] = self.phone
    d['mobile'] = self.mobile
    d['email'] = self.email
    d['payrollcode'] = self.payrollcode
    return d
