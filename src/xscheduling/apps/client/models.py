from datetime import datetime
from django.db import models
from django.db.models import Q
from django.conf import settings
from django.utils.text import capfirst
from django.utils.translation import ugettext_lazy as _
from geocoders.google import geocoder
from workflowmax.client.models import Client as WorkflowmaxClient, Contact as WorkflowmaxContact

class NotImplementedException(Exception):
  "Method not implemented"
  pass

class WorkflowmaxBase(models.Model):
  wm_id = models.CharField(_('worfkflowmax id'), max_length=255, default='', blank=True)
  class Meta:
    abstract = True

  def wm_sync(self):
    raise NotImplementedException()

  def wm_import(self, wm_object):
    raise NotImplementedException()

  def wm_delete(self):
    raise NotImplementedException()

class ContactBase(WorkflowmaxBase):
  MR = 1
  MS = 2
  MRS = 3
  SALUTATION_LIST = (
    (MR, capfirst(_('mr'))),
    (MS, capfirst(_('ms'))),
    (MRS, capfirst(_('mrs'))),
  )
  salutation = models.PositiveSmallIntegerField(_('salutation'), max_length=3, choices = SALUTATION_LIST, default=MR)
  name = models.CharField(_('name'), max_length=255, help_text=_('(Ex. John Smith)'))
  mobile = models.CharField(_('mobile'), max_length=255, null=True, blank=True, help_text=_('(Ex. 020828129)'))
  email = models.EmailField(_('email'), null=True, blank=True)
  phone = models.CharField(_('phone'), max_length=255, null=True, blank=True, help_text=_('(Ex. 020828129)'))
  position = models.CharField(_('position'), max_length=255, null=True, blank=True, help_text=_('(Ex. HR manager)'))

  class Meta:
    abstract = True
    ordering = ['name']
    verbose_name = _('contact')
    verbose_name_plural = _('contacts')

  def __unicode__(self):
    return self.name

  def wm_import(self, wm_contact):
    self.wm_id = wm_contact.id
    self.name = wm_contact.name
    self.mobile = wm_contact.mobile
    self.email = wm_contact.email
    self.phone = wm_contact.phone
    self.position = wm_contact.position
  
class Contact(ContactBase):
  client = models.ForeignKey('Client', verbose_name="client", related_name='contacts')

  def wm_sync(self):
    if self.name and self.client.wm_id:
      wm_contact = WorkflowmaxContact()
      if self.wm_id:
        wm_contact.id = int(self.wm_id)
      else:
        wm_contact.owner_id = int(self.client.wm_id)      
      wm_contact.name = self.name
      wm_contact.mobile = self.mobile
      wm_contact.email = self.email
      wm_contact.phone = self.phone
      wm_contact.position = self.position
      wm_contact = wm_contact.save()
      if not self.wm_id:
        self.wm_id = wm_contact.id
        self.save()

class NoteBase(models.Model):
  title = models.CharField(_('title'), max_length=255, help_text=_('(Ex. Angry dog)'))
  text = models.TextField(_('text'))
  folder = models.CharField(_('folder'), max_length=255, null=True, blank=True)
  date = models.DateTimeField(_('date'), null=True, blank=True, default=datetime.now(), help_text=_('(Format: YYYY-MM-DD HH:MM:SS)'))
  created_by = models.CharField(_('created by'), max_length=255, null=True, blank=True)
  public = models.BooleanField(_('public'), default=True)

  class Meta:
    abstract = True
    ordering = ['title']
    verbose_name = _('note')
    verbose_name_plural = _('notes')

  def __unicode__(self):
    return self.title

  def wm_sync(self):
    raise NotImplementedException()

  def wm_import(self, wm_object):
    self.title = wm_object.title
    self.text = wm_object.text
    self.folder = wm_object.folder
    self.date = wm_object.date
    self.created_by = wm_object.created_by

class Note(NoteBase):
  client = models.ForeignKey('Client', verbose_name="client", related_name='notes')

class Address(models.Model):
  postcode = models.CharField(max_length=10, help_text=_('(Ex. TW8 8EL)'))
  address = models.CharField(max_length=100, help_text=_('(Ex. 11 Moorings House Tallow Road)'))
  city = models.CharField(max_length=20, help_text=_('(Ex. Brentford)'))
  county = models.CharField(max_length=20, default='Greater London', help_text=_('(Ex. Greater London)'))
  country = models.CharField(max_length=10, default='UK', help_text=_('(Ex. UK)'))
  latitude = models.DecimalField(max_digits=13, decimal_places=10, blank=True, null=True)
  longitude = models.DecimalField(max_digits=13, decimal_places=10, blank=True, null=True)
  
  class Meta:
    verbose_name = _('address')
    verbose_name_plural = _('address')

  def __unicode__(self):
    return '%s, %s, %s, %s, %s' % (self.postcode, self.address, self.city, self.county, self.country)

  def save(self, *args, **kwargs):
    geocode = geocoder(settings.GOOGLE_GEOCODER_KEY)
    location_data = geocode(str(self))
    try:
      coords = location_data[1]
      self.latitude = str(coords[0])
      self.longitude = str(coords[1])
    except IndexError:
      pass
    super(Address, self).save(*args, **kwargs)

  def wm_import(self, wm_address):
    if wm_address:
      try:
        (self.postcode, self.address, self.city, self.county, self.country) = wm_address.split(',')
      except ValueError:
        pass

class ClientBase(WorkflowmaxBase):
  COMPANY = 4
  SALUTATION_LIST = (
    (ContactBase.MR, capfirst(_('mr'))),
    (ContactBase.MS, capfirst(_('ms'))),
    (ContactBase.MRS, capfirst(_('mrs'))),
    (COMPANY, capfirst(_('company'))),
  )
  salutation = models.CharField(_('salutation'), max_length=10, choices = SALUTATION_LIST, default=COMPANY)
  name = models.CharField(_('name'), max_length=255, help_text=_('(Ex. John Smith or Destroyer inc.)'))
  email = models.EmailField(_('email'), null=True, blank=True)
  address = models.OneToOneField(Address, related_name='%(class)s_address', verbose_name=_('address'), blank=True, null=True)
  postal_address = models.OneToOneField(Address, related_name='%(class)s_postal_address', verbose_name=_('postal address'), blank=True, null=True)
  phone = models.CharField(_('phone'), max_length=255, null=True, blank=True, help_text=_('(Ex. 020828129)'))
  fax = models.CharField(_('fax'), max_length=255, null=True, blank=True, help_text=_('(Ex. 020828129)'))
  website = models.URLField(_('website'), null=True, blank=True, help_text=_('(Ex. www.xsdf.com)'))
  referral_source = models.CharField(_('referral source'), max_length=255, null=True, blank=True)

  class Meta:
    abstract = True

  def __unicode__(self):
    return self.name

  def save(self, *args, **kwargs):
    if not self.address:
      address = Address()
      address.save()
      self.address = address
    if not self.postal_address:
      postal_address = Address()
      postal_address.save()
      self.postal_address = postal_address
    super(ClientBase, self).save(*args, **kwargs)

  def delete(self):
    super(ClientBase, self).delete()
    self.address.delete()
    self.postal_address.delete()

  def wm_import_contacts(self, wm_client):
    raise NotImplementedException()

  def wm_import_notes(self, wm_client):
    raise NotImplementedException()

  # we have to include save() here, because of OneToOne field behaviour
  def wm_import(self, wm_object):
    address = Address()
    address.wm_import(wm_object.address)
    address.save()
    self.address = address
    postal_address = Address()
    postal_address.wm_import(wm_object.postal_address)
    postal_address.save()
    self.postal_address = postal_address
    self.wm_id = wm_object.id
    self.name = wm_object.name
    self.phone = wm_object.phone
    self.fax = wm_object.fax
    self.website = wm_object.website
    self.referral_source = wm_object.referral_source
    self.save()
    self.wm_import_contacts(wm_object)
    self.wm_import_notes(wm_object)

class ClientManager(models.Manager):
  def search(self, string):
    clients = Client.objects.filter(
      Q(name__icontains=string) | 
      Q(email__icontains=string) |
      Q(phone__icontains=string)
      )
    unique_clients = dict()
    for c in clients:
      unique_clients[c.id] = c
    addresses = Address.objects.filter(
      Q(postcode__icontains=string) | 
      Q(address__icontains=string) | 
      Q(city__icontains=string)
    )
    for addr in addresses:
      if hasattr(addr, 'client_address'):
        unique_clients[addr.client_address.id] = addr.client_address
      if hasattr(addr, 'client_postal_address'):
        unique_clients[addr.client_postal_address.id] = addr.client_postal_address
    clients = unique_clients.values()
    return clients

class Client(ClientBase): 
  objects = ClientManager()

  class Meta:
    verbose_name = _('client')
    verbose_name_plural = _('clients')

  def wm_sync(self):
    if self.name:
      wm_client = WorkflowmaxClient()
      if self.wm_id:
        wm_client.id = int(self.wm_id)
      wm_client.name = self.name
      wm_client.address = str(self.address)
      wm_client.postal_address = str(self.postal_address)
      wm_client.phone = self.phone
      wm_client.fax = self.fax
      wm_client.website = self.website
      wm_client.referral_source = self.referral_source
      wm_client = wm_client.save()
      if not self.wm_id:
        self.wm_id = wm_client.id
        self.save()
      if self.contacts.all():
        for contact in self.contacts.all():
          contact.wm_sync()

  def wm_delete(self):
    if self.wm_id:
      wm_client = WorkflowmaxClient.objects.get(id=self.wm_id)
      wm_client.delete()

  def wm_import_contacts(self, wm_client):
    for wm_contact in wm_client.contacts:
      contact = Contact()
      contact.client = self
      contact.wm_import(wm_contact)
      contact.save()

  def wm_import_notes(self, wm_client):
    for wm_note in wm_client.notes:
      note = Note()
      note.client = self
      note.wm_import(wm_note)
      note.save()


