from django.db import models
import xml_models
import rest_client
from BeautifulSoup import BeautifulStoneSoup

class ResponseStatusError(Exception):
    def __init__(self, error):
        Exception.__init__(self, "ResponseStatusError: %s" % error)

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

class ClientManager(object):
  model = "Client"

  def all(self):
    response = rest_client.Client("").GET("http://api.workflowmax.com/client.api/list?apiKey=14C10292983D48CE86E1AA1FE0F8DDFE&accountKey=F44B9DB0ED704D7AB0A6AA2AC09CB3EA") 
    soup = BeautifulStoneSoup(response.content)
    objects = list()
    for client_xml in soup.clients.contents:
      objects.append(globals()[self.model](xml=str(client_xml)))
    return objects

class Client(xml_models.Model):
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
  
  client_objects = ClientManager()

  def validate_on_load(self):
    soup = BeautifulStoneSoup(self._xml)
    if soup.status and soup.status.contents[0].lower() == 'error':
      raise ResponseStatusError(soup.errordescription.contents[0])
    self._xml = str(soup.client)


