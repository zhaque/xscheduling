from django.db import models
import xml_models
import rest_client
from BeautifulSoup import BeautifulStoneSoup, BeautifulSoup, Tag, NavigableString
from django.conf import settings
from workflowmax.exceptions import ResponseStatusError, InvalidObjectType

from workflowmax.client.models import Note

class XmlContact(xml_models.Model):
  id = xml_models.IntField(xpath="/contact/id")
  name = xml_models.CharField(xpath="/contact/name")
  mobile = xml_models.CharField(xpath="/contact/mobile")
  email = xml_models.CharField(xpath="/contact/email")
  phone = xml_models.CharField(xpath="/contact/phone")
  position = xml_models.CharField(xpath="/contact/position")
  
  finders = { (id,): "http://api.workflowmax.com/supplier.api/contact/%s?apiKey=%s&accountKey=%s" % ('%s', settings.WORKFLOWMAX_APIKEY, settings.WORKFLOWMAX_ACCOUNTKEY)} 

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
  put = "http://api.workflowmax.com/supplier.api/contact/%s?apiKey=%s&accountKey=%s" % ('%s', settings.WORKFLOWMAX_APIKEY, settings.WORKFLOWMAX_ACCOUNTKEY)
  post = "http://api.workflowmax.com/supplier.api/contact?apiKey=%s&accountKey=%s" % (settings.WORKFLOWMAX_APIKEY, settings.WORKFLOWMAX_ACCOUNTKEY)

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
      supplier_tag = Tag(soup, 'Supplier')
      supplier_id_tag = Tag(soup, 'ID')
      supplier_id_tag.insert(0, NavigableString('%d' % self.owner_id))
      supplier_tag.insert(0, supplier_id_tag)
      contact_tag.insert(i, supplier_tag)
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

class XmlSupplierManager(object):
  list_url = "http://api.workflowmax.com/supplier.api/list?apiKey=%s&accountKey=%s" % (settings.WORKFLOWMAX_APIKEY, settings.WORKFLOWMAX_ACCOUNTKEY)

  def all(self):
    response = rest_client.Client("").GET(self.list_url)
    soup = BeautifulStoneSoup(response.content)
    if soup.status and soup.status.contents[0].lower() == 'error':
      raise ResponseStatusError(soup.errordescription.contents[0])
    objects = list()
    for object_xml in soup.suppliers.contents:
      objects.append(XmlSupplier(xml=str(object_xml)))
    return objects

class XmlSupplier(xml_models.Model):
  id = xml_models.IntField(xpath="/supplier/id")
  name = xml_models.CharField(xpath="/supplier/name")
  address = xml_models.CharField(xpath="/supplier/address")
  postal_address = xml_models.CharField(xpath="/supplier/postaladdress")
  phone = xml_models.CharField(xpath="/supplier/phone")
  fax = xml_models.CharField(xpath="/supplier/fax")
  website = xml_models.CharField(xpath="/supplier/website")
  referral_source = xml_models.CharField(xpath="/supplier/referralsource")
  contacts = xml_models.Collection(Contact, order_by="name", xpath="/supplier/contacts/contact")
  notes = xml_models.Collection(Note, order_by="title", xpath="/supplier/notes/note")

  finders = { (id,): "http://api.workflowmax.com/supplier.api/get/%s?apiKey=%s&accountKey=%s" % ('%s', settings.WORKFLOWMAX_APIKEY, settings.WORKFLOWMAX_ACCOUNTKEY)}
  
  supplier_objects = XmlSupplierManager()

  def validate_on_load(self):
    soup = BeautifulStoneSoup(self._xml)
    if soup.status and soup.status.contents[0].lower() == 'error':
      raise ResponseStatusError(soup.errordescription.contents[0])
    self._xml = str(soup.supplier)


class SupplierManager(object):
  def all(self):
    xml_objects = XmlSupplier.supplier_objects.all()
    res = list()
    for xml_object in xml_objects:
      res.append(Supplier(xml_object))
    return res

  def get(self, **kw):
    return Supplier(XmlSupplier.objects.get(**kw))

class Supplier(object):
  objects = SupplierManager()
  put = "http://api.workflowmax.com/supplier.api/update?apiKey=%s&accountKey=%s" % (settings.WORKFLOWMAX_APIKEY, settings.WORKFLOWMAX_ACCOUNTKEY)
  post = "http://api.workflowmax.com/supplier.api/add?apiKey=%s&accountKey=%s" % (settings.WORKFLOWMAX_APIKEY, settings.WORKFLOWMAX_ACCOUNTKEY)

  def __init__(self, xml_object=None, xml=None):
    self.xml_object = xml_object
    if xml_object and not isinstance(xml_object, xml_models.Model):
      raise InvalidObjectType('object is not child of xml_models.Model')
    if xml:
      self.xml_object = XmlSupplier(xml=xml)

  def __getattr__(self, name):
    return getattr(self.xml_object, name)

  def save(self):
    soup = BeautifulSoup()
    supplier_tag = Tag(soup, 'Supplier')
    soup.insert(0, supplier_tag)
    i = 0
    method = "POST"
    try:
      id_tag = Tag(soup, 'ID')
      id_tag.insert(0, NavigableString('%d' % self.id))
      supplier_tag.insert(i, id_tag)
      i = i+1
      method = "PUT"
    except AttributeError:
      pass
    
    try:
      name_tag = Tag(soup, 'Name')
      name_tag.insert(0, NavigableString(self.name))
      supplier_tag.insert(i, name_tag)
      i = i+1
    except AttributeError:
      raise ValueError("You must provide supplier's name.")  
    
    try:
      if self.address:
        address_tag = Tag(soup, 'Address')
        address_tag.insert(0, NavigableString(self.address))
        supplier_tag.insert(i, address_tag)
        i = i+1
    except AttributeError:
      pass
    
    try:
      if self.postal_address:
        postal_address_tag = Tag(soup, 'PostalAddress')
        postal_address_tag.insert(0, NavigableString(self.postal_address))
        supplier_tag.insert(i, postal_address_tag)
        i = i+1
    except AttributeError:
      pass
    
    try:
      if self.phone:
        phone_tag = Tag(soup, 'Phone')
        phone_tag.insert(0, NavigableString(self.phone))
        supplier_tag.insert(i, phone_tag)
        i = i+1
    except AttributeError:
      pass

    try:
      if self.fax:
        fax_tag = Tag(soup, 'Fax')
        fax_tag.insert(0, NavigableString(self.fax))
        supplier_tag.insert(i, fax_tag)
        i = i+1
    except AttributeError:
      pass

    try:
      if self.website:
        website_tag = Tag(soup, 'WebSite')
        website_tag.insert(0, NavigableString(self.website))
        supplier_tag.insert(i, website_tag)
        i = i+1
    except AttributeError:
      pass
    
    try:
      if self.referral_source:
        referral_source_tag = Tag(soup, 'ReferralSource')
        referral_source_tag.insert(0, NavigableString(self.referral_source))
        supplier_tag.insert(i, referral_source_tag)
    except AttributeError:
      pass

    if method == "PUT":
      response = rest_client.Client("").PUT(self.put, str(soup))
    else:
      response = rest_client.Client("").POST(self.post, str(soup))
    return Supplier(xml=response.content)

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
