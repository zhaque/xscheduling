from django.db import models
from django.utils.translation import ugettext_lazy as _
from workflowmax.client.models import Client as WorkflowmaxClient, Contact as WorkflowmaxContact

class WorkflowmaxBase(models.Model):
  wm_id = models.CharField(_('worfkflowmax id'), max_length=255, default='', blank=True)

class Contact(WorkflowmaxBase):
  name = models.CharField(_('name'), max_length=255)
  mobile = models.CharField(_('mobile'), max_length=255, null=True, blank=True)
  email = models.EmailField(_('email'), null=True, blank=True)
  phone = models.CharField(_('phone'), max_length=255, null=True, blank=True)
  position = models.CharField(_('position'), max_length=255, null=True, blank=True)
  client = models.ForeignKey('Client', verbose_name="client", related_name='contacts')

  class Meta:
    ordering = ['name']
    verbose_name = _('contact')
    verbose_name_plural = _('contacts')

  def __unicode__(self):
    return self.name

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

  def import_wmcontact(self, wm_contact):
    self.wm_id = wm_contact.id
    self.name = wm_contact.name
    self.mobile = wm_contact.mobile
    self.email = wm_contact.email
    self.phone = wm_contact.phone
    self.position = wm_contact.position
  

class Note(models.Model):
  title = models.CharField(_('title'), max_length=255)
  text = models.TextField(_('text'))
  folder = models.CharField(_('folder'), max_length=255, null=True, blank=True)
  date = models.DateTimeField(_('date'), null=True, blank=True)
  created_by = models.CharField(_('created_by'), max_length=255, null=True, blank=True)
  client = models.ForeignKey('Client', verbose_name="client", related_name='notes')

  class Meta:
    ordering = ['title']
    verbose_name = _('note')
    verbose_name_plural = _('notes')

  def __unicode__(self):
    return self.title

class Address(models.Model):
  postcode = models.CharField(max_length=10)
  address = models.CharField(max_length=100)
  city = models.CharField(max_length=20)
  county = models.CharField(max_length=20, default='Greater London')
  country = models.CharField(max_length=10, default='UK')
  latitude = models.DecimalField(max_digits=13, decimal_places=10, blank=True, null=True)
  longitude = models.DecimalField(max_digits=13, decimal_places=10, blank=True, null=True)
  
  class Meta:
    verbose_name = _('address')
    verbose_name_plural = _('address')

  def __unicode__(self):
    return '%s, %s, %s, %s, %s' % (self.postcode, self.address, self.city, self.county, self.country)

  def import_wmaddress(self, wm_address):
    if wm_address:
      try:
        (self.postcode, self.address, self.city, self.county, self.country) = wm_address.split(',')
      except ValueError:
        pass

class Client(WorkflowmaxBase):
  name = models.CharField(_('name'), max_length=255)
  address = models.OneToOneField(Address, related_name='client_address', verbose_name=_('address'), blank=True, null=True)
  postal_address = models.OneToOneField(Address, related_name='client_postal_address', verbose_name=_('postal address'), blank=True, null=True)
  phone = models.CharField(_('phone'), max_length=255, null=True, blank=True)
  fax = models.CharField(_('fax'), max_length=255, null=True, blank=True)
  website = models.URLField(_('website'), null=True, blank=True)
  referral_source = models.CharField(_('referral source'), max_length=255, null=True, blank=True)

  class Meta:
    verbose_name = _('client')
    verbose_name_plural = _('clients')

  def __unicode__(self):
    return self.name

  def save(self):
    if not self.address:
      address = Address()
      address.save()
      self.address = address
    if not self.postal_address:
      postal_address = Address()
      postal_address.save()
      self.postal_address = postal_address
    super(Client, self).save()

  def delete(self):
    super(Client, self).delete()
    self.address.delete()
    self.postal_address.delete()

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

  # we have to include save() here (and only this model), because of OneToOne field behaviour
  def import_wmclient(self, wm_client):
    address = Address()
    address.import_wmaddress(wm_client.address)
    address.save()
    self.address = address
    postal_address = Address()
    postal_address.import_wmaddress(wm_client.postal_address)
    postal_address.save()
    self.postal_address = postal_address
    self.wm_id = wm_client.id
    self.name = wm_client.name
    self.phone = wm_client.phone
    self.fax = wm_client.fax
    self.website = wm_client.website
    self.referral_source = wm_client.referral_source
    self.save()
    for wm_contact in wm_client.contacts:
      contact = Contact()
      contact.client = self
      contact.import_wmcontact(wm_contact)
      contact.save()

