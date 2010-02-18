from django.db import models
import xml_models
import rest_client
from BeautifulSoup import BeautifulStoneSoup, BeautifulSoup, Tag, NavigableString

class ResponseStatusError(Exception):
    def __init__(self, error):
        Exception.__init__(self, "ResponseStatusError: %s" % error)

class InvalidObjectType(Exception):
    def __init__(self, error):
        Exception.__init__(self, "InvalidObjectType: %s" % error)

class Contact(xml_models.Model):
  id = xml_models.IntField(xpath="/contact/id")
  name = xml_models.CharField(xpath="/contact/name")
  mobile = xml_models.CharField(xpath="/contact/mobile")
  email = xml_models.CharField(xpath="/contact/email")
  phone = xml_models.CharField(xpath="/contact/phone")
  position = xml_models.CharField(xpath="/contact/position")
  
  finders = { (id,): "http://api.workflowmax.com/client.api/contact/%s?apiKey=14C10292983D48CE86E1AA1FE0F8DDFE&accountKey=F44B9DB0ED704D7AB0A6AA2AC09CB3EA"} 

  def validate_on_load(self):
    soup = BeautifulStoneSoup(self._xml)
    if soup.status and soup.status.contents[0].lower() == 'error':
      raise ResponseStatusError(soup.errordescription.contents[0])
    self._xml = str(soup.contact)

class Note(xml_models.Model):
  title = xml_models.CharField(xpath="/note/title")
  text = xml_models.CharField(xpath="/note/text")
  folder = xml_models.CharField(xpath="/note/folder")
  date = xml_models.DateField(xpath="/note/date", date_format="%Y-%m-%dT%H:%M:%S")
  created_by = xml_models.CharField(xpath="/note/createdBy")

class XmlClientManager(object):

  def all(self):
    response = rest_client.Client("").GET("http://api.workflowmax.com/client.api/list?apiKey=14C10292983D48CE86E1AA1FE0F8DDFE&accountKey=F44B9DB0ED704D7AB0A6AA2AC09CB3EA") 
    soup = BeautifulStoneSoup(response.content)
    if soup.status and soup.status.contents[0].lower() == 'error':
      raise ResponseStatusError(soup.errordescription.contents[0])
    objects = list()
    for client_xml in soup.clients.contents:
      objects.append(XmlClient(xml=str(client_xml)))
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

  finders = { (id,): "http://api.workflowmax.com/client.api/get/%s?apiKey=14C10292983D48CE86E1AA1FE0F8DDFE&accountKey=F44B9DB0ED704D7AB0A6AA2AC09CB3EA"}
  
  client_objects = XmlClientManager()

  def validate_on_load(self):
    soup = BeautifulStoneSoup(self._xml)
    if soup.status and soup.status.contents[0].lower() == 'error':
      raise ResponseStatusError(soup.errordescription.contents[0])
    self._xml = str(soup.client)


class ClientManager(object):
  def all(self):
    cl = XmlClient.client_objects.all()
    res = list()
    for xml_client in cl:
      res.append(Client(xml_client))
    return res

  def filter(self, **kw):
    return XmlClient.objects.filter(**kw)

  def get(self, **kw):
    return Client(XmlClient.objects.get(**kw))

class Client(object):
  objects = ClientManager()
  put = "http://api.workflowmax.com/client.api/update?apiKey=14C10292983D48CE86E1AA1FE0F8DDFE&accountKey=F44B9DB0ED704D7AB0A6AA2AC09CB3EA"
  post = "http://api.workflowmax.com/client.api/add?apiKey=14C10292983D48CE86E1AA1FE0F8DDFE&accountKey=F44B9DB0ED704D7AB0A6AA2AC09CB3EA"

  def __init__(self, xml_client=None):
    if not xml_client: return
    if not isinstance(xml_client, xml_models.Model):
      raise InvalidObjectType('object is not child of xml_models.Model')
    self.xml_client = xml_client

  def __getattr__(self, name):
    if not hasattr(self, 'xml_client'):
      raise AttributeError()
    return getattr(self.xml_client, name)

#  def __setattr__(self, name, value):
#    if name == 'id':
#      raise AttributeError('You cannot set ID manually')
  
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
        referral_source_tag = Tag(soup, 'ReferralSourcee')
        referral_source_tag.insert(0, NavigableString(self.referral_source))
        client_tag.insert(i, referral_source_tag)
    except AttributeError:
      pass

    if method == "PUT":
      response = rest_client.Client("").PUT(self.put, str(soup))
    else:
      response = rest_client.Client("").POST(self.post, str(soup))
    return response.content

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
