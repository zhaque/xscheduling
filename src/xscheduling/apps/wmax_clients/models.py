from django.db import models
import xml_models

class Contact(xml_models.Model):
  id = xml_models.IntField(xpath="/Contact/ID")
  name = xml_models.CharField(xpath="/Contact/Name")
  mobile = xml_models.CharField(xpath="/Contact/Mobile")
  email = xml_models.CharField(xpath="/Contact/Email")
  phone = xml_models.CharField(xpath="/Contact/Phone")
  position = xml_models.CharField(xpath="/Contact/Position")
  
  finders = { (id,): "http://api.workflowmax.com/client.api/contact/%s?apiKey=14C10292983D48CE86E1AA1FE0F8DDFE&accountKey=F44B9DB0ED704D7AB0A6AA2AC09CB3EA"} 

class Note(xml_models.Model):
  title = xml_models.CharField(xpath="/Note/Title")
  text = xml_models.CharField(xpath="/Note/Text")
  folder = xml_models.CharField(xpath="/Note/Folder")
  date = xml_models.DateField(xpath="/Note/Date", date_format="%Y-%m-%dT%H:%M:%S")
  created_by = xml_models.CharField(xpath="/Note/CreatedBy")

class Client(xml_models.Model):
  id = xml_models.IntField(xpath="/Response/Client/ID")
  name = xml_models.CharField(xpath="/Response/Client/Name")
  address = xml_models.CharField(xpath="/Response/Client/Address")
  postal_address = xml_models.CharField(xpath="/Response/Client/PostalAddress")
  phone = xml_models.CharField(xpath="/Response/Client/Phone")
  fax = xml_models.CharField(xpath="/Response/Client/Fax")
  website = xml_models.CharField(xpath="/Response/Client/Website")
  referral_source = xml_models.CharField(xpath="/Response/Client/ReferralSource")
  contacts = xml_models.Collection(Contact, order_by="name", xpath="/Response/Client/Contacts/Contact")
  notes = xml_models.Collection(Note, order_by="title", xpath="/Response/Client/Notes/Note")

  finders = { (id,): "http://api.workflowmax.com/client.api/get/%s?apiKey=14C10292983D48CE86E1AA1FE0F8DDFE&accountKey=F44B9DB0ED704D7AB0A6AA2AC09CB3EA"} 
