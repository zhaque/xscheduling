from django.db import models
import xml_models
import rest_client
from BeautifulSoup import BeautifulStoneSoup, BeautifulSoup, Tag, NavigableString
from django.conf import settings
from workflowmax.exceptions import ResponseStatusError, InvalidObjectType

class XmlContact(xml_models.Model):
  id = xml_models.IntField(xpath="/contact/id")
  name = xml_models.CharField(xpath="/contact/name")
  mobile = xml_models.CharField(xpath="/contact/mobile")
  email = xml_models.CharField(xpath="/contact/email")
  phone = xml_models.CharField(xpath="/contact/phone")
  position = xml_models.CharField(xpath="/contact/position")
  
  finders = { (id,): "http://api.workflowmax.com/client.api/contact/%s?apiKey=%s&accountKey=%s" % ('%s', settings.WORKFLOWMAX_APIKEY, settings.WORKFLOWMAX_ACCOUNTKEY)} 

  def validate_on_load(self):
    soup = BeautifulStoneSoup(self._xml)
    if soup.status and soup.status.contents[0].lower() == 'error':
      raise ResponseStatusError(soup.errordescription.contents[0])
    self._xml = str(soup.contact)

class ContactManager(object):
  def get(self, **kw):
    return Contact(XmlContact.objects.get(**kw))

class Contact(object):
  objects = ContactManager()
  put = "http://api.workflowmax.com/client.api/contact/%s?apiKey=%s&accountKey=%s" % ('%s', settings.WORKFLOWMAX_APIKEY, settings.WORKFLOWMAX_ACCOUNTKEY)
  post = "http://api.workflowmax.com/client.api/contact?apiKey=%s&accountKey=%s" % (settings.WORKFLOWMAX_APIKEY, settings.WORKFLOWMAX_ACCOUNTKEY)

  def __init__(self, xml_contact=None, xml=None):
    self.xml_contact = xml_contact
    if xml_contact and not isinstance(xml_contact, xml_models.Model):
      raise InvalidObjectType('object is not child of xml_models.Model')
    if xml:
      self.xml_contact = XmlContact(xml=xml)

  def __getattr__(self, name):
    return getattr(self.xml_contact, name)

  def save(self):
    soup = BeautifulSoup()
    contact_tag = Tag(soup, 'Contact')
    soup.insert(0, contact_tag)
    i = 0
    method = "PUT"

    try:
      id_tag = Tag(soup, 'ID')
      id_tag.insert(0, NavigableString('%d' % self.id))
      contact_tag.insert(i, id_tag)
      i = i+1
    except AttributeError:
      pass

    try:
      client_tag = Tag(soup, 'Client')
      client_id_tag = Tag(soup, 'ID')
      client_id_tag.insert(0, NavigableString('%d' % self.owner_id))
      client_tag.insert(0, client_id_tag)
      contact_tag.insert(i, client_tag)
      i = i+1
      method = "POST"
    except AttributeError:
      pass
    
    try:
      name_tag = Tag(soup, 'Name')
      name_tag.insert(0, NavigableString(self.name))
      contact_tag.insert(i, name_tag)
      i = i+1
    except AttributeError:
      raise ValueError("You must provide client's name.")  
    
    try:
      if self.mobile:
        mobile_tag = Tag(soup, 'Mobile')
        mobile_tag.insert(0, NavigableString(self.mobile))
        contact_tag.insert(i, mobile_tag)
        i = i+1
    except AttributeError:
      pass
    
    try:
      if self.email:
        email_tag = Tag(soup, 'Email')
        email_tag.insert(0, NavigableString(self.email))
        contact_tag.insert(i, email_tag)
        i = i+1
    except AttributeError:
      pass
    
    try:
      if self.phone:
        phone_tag = Tag(soup, 'Phone')
        phone_tag.insert(0, NavigableString(self.phone))
        contact_tag.insert(i, phone_tag)
        i = i+1
    except AttributeError:
      pass

    try:
      if self.position:
        position_tag = Tag(soup, 'Position')
        position_tag.insert(0, NavigableString(self.position))
        contact_tag.insert(i, position_tag)
        i = i+1
    except AttributeError:
      pass

    if method == "PUT":
      response = rest_client.Client("").PUT(self.put % self.id, str(soup))
    else:
      response = rest_client.Client("").POST(self.post, str(soup))
    return Contact(xml=response.content)

  def to_dict(self):
    d = dict()
    d['name'] = self.name
    d['mobile'] = self.mobile
    d['email'] = self.email
    d['phone'] = self.phone
    d['position'] = self.position
    return d

class Note(xml_models.Model):
  title = xml_models.CharField(xpath="/note/title")
  text = xml_models.CharField(xpath="/note/text")
  folder = xml_models.CharField(xpath="/note/folder")
  date = xml_models.DateField(xpath="/note/date", date_format="%Y-%m-%dT%H:%M:%S")
  created_by = xml_models.CharField(xpath="/note/createdBy")

class XmlClientManager(object):
  list_url = "http://api.workflowmax.com/client.api/list?detailed=%s&apiKey=%s&accountKey=%s" % ('%s', settings.WORKFLOWMAX_APIKEY, settings.WORKFLOWMAX_ACCOUNTKEY)

  def all(self, detailed=False):
    response = rest_client.Client("").GET(self.list_url % str(detailed).lower())
    soup = BeautifulStoneSoup(response.content)
    if soup.status and soup.status.contents[0].lower() == 'error':
      raise ResponseStatusError(soup.errordescription.contents[0])
    objects = list()
    for object_xml in soup.clients.contents:
      objects.append(XmlClient(xml=str(object_xml)))
    return objects

class XmlClient(xml_models.Model):
  id = xml_models.IntField(xpath="/client/id")
  name = xml_models.CharField(xpath="/client/name")
  address = xml_models.CharField(xpath="/client/address")
  postal_address = xml_models.CharField(xpath="/client/postaladdress")
  phone = xml_models.CharField(xpath="/client/phone")
  fax = xml_models.CharField(xpath="/client/fax")
  website = xml_models.CharField(xpath="/client/website")
  referral_source = xml_models.CharField(xpath="/client/referralsource")
  contacts = xml_models.Collection(Contact, order_by="name", xpath="/client/contacts/contact")
  notes = xml_models.Collection(Note, order_by="title", xpath="/client/notes/note")

  finders = { (id,): "http://api.workflowmax.com/client.api/get/%s?apiKey=%s&accountKey=%s" % ('%s', settings.WORKFLOWMAX_APIKEY, settings.WORKFLOWMAX_ACCOUNTKEY)}
  
  client_objects = XmlClientManager()

  def validate_on_load(self):
    soup = BeautifulStoneSoup(self._xml)
    if soup.status and soup.status.contents[0].lower() == 'error':
      raise ResponseStatusError(soup.errordescription.contents[0])
    self._xml = str(soup.client)


class ClientManager(object):
  def all(self, detailed=True):
    cl = XmlClient.client_objects.all(detailed)
    res = list()
    for xml_client in cl:
      res.append(Client(xml_client))
    return res

  def get(self, **kw):
    return Client(XmlClient.objects.get(**kw))

class Client(object):
  objects = ClientManager()
  put = "http://api.workflowmax.com/client.api/update?apiKey=%s&accountKey=%s" % (settings.WORKFLOWMAX_APIKEY, settings.WORKFLOWMAX_ACCOUNTKEY)
  post = "http://api.workflowmax.com/client.api/add?apiKey=%s&accountKey=%s" % (settings.WORKFLOWMAX_APIKEY, settings.WORKFLOWMAX_ACCOUNTKEY)
  delete_url = "http://api.workflowmax.com/client.api/delete?apiKey=%s&accountKey=%s" % (settings.WORKFLOWMAX_APIKEY, settings.WORKFLOWMAX_ACCOUNTKEY)


  def __init__(self, xml_object=None, xml=None):
    self.xml_object = xml_object
    if xml_object and not isinstance(xml_object, xml_models.Model):
      raise InvalidObjectType('object is not child of xml_models.Model')
    if xml:
      self.xml_object = XmlClient(xml=xml)

  def __getattr__(self, name):
    return getattr(self.xml_object, name)

  def save(self):
    soup = BeautifulSoup()
    client_tag = Tag(soup, 'Client')
    soup.insert(0, client_tag)
    i = 0
    method = "POST"
    try:
      id_tag = Tag(soup, 'ID')
      id_tag.insert(0, NavigableString('%d' % self.id))
      client_tag.insert(i, id_tag)
      i = i+1
      method = "PUT"
    except AttributeError:
      pass
    
    try:
      name_tag = Tag(soup, 'Name')
      name_tag.insert(0, NavigableString(self.name))
      client_tag.insert(i, name_tag)
      i = i+1
    except AttributeError:
      raise ValueError("You must provide client's name.")  
    
    try:
      if self.address:
        address_tag = Tag(soup, 'Address')
        address_tag.insert(0, NavigableString(self.address))
        client_tag.insert(i, address_tag)
        i = i+1
    except AttributeError:
      pass
    
    try:
      if self.postal_address:
        postal_address_tag = Tag(soup, 'PostalAddress')
        postal_address_tag.insert(0, NavigableString(self.postal_address))
        client_tag.insert(i, postal_address_tag)
        i = i+1
    except AttributeError:
      pass
    
    try:
      if self.phone:
        phone_tag = Tag(soup, 'Phone')
        phone_tag.insert(0, NavigableString(self.phone))
        client_tag.insert(i, phone_tag)
        i = i+1
    except AttributeError:
      pass

    try:
      if self.fax:
        fax_tag = Tag(soup, 'Fax')
        fax_tag.insert(0, NavigableString(self.fax))
        client_tag.insert(i, fax_tag)
        i = i+1
    except AttributeError:
      pass

    try:
      if self.website:
        website_tag = Tag(soup, 'WebSite')
        website_tag.insert(0, NavigableString(self.website))
        client_tag.insert(i, website_tag)
        i = i+1
    except AttributeError:
      pass
    
    try:
      if self.referral_source:
        referral_source_tag = Tag(soup, 'ReferralSource')
        referral_source_tag.insert(0, NavigableString(self.referral_source))
        client_tag.insert(i, referral_source_tag)
    except AttributeError:
      pass

    if method == "PUT":
      response = rest_client.Client("").PUT(self.put, str(soup))
    else:
      response = rest_client.Client("").POST(self.post, str(soup))
    return Client(xml=response.content)

  def delete(self):
    soup = BeautifulSoup()
    client_tag = Tag(soup, 'Client')
    soup.insert(0, client_tag)
    try:
      id_tag = Tag(soup, 'ID')
      id_tag.insert(0, NavigableString('%d' % self.id))
      client_tag.insert(0, id_tag)
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
    d['postal_address'] = self.postal_address
    d['phone'] = self.phone
    d['fax'] = self.fax
    d['website'] = self.website
    d['referral_source'] = self.referral_source
    return d
