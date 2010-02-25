from django.db import models
from django.utils.translation import ugettext_lazy as _

class Contact(models.Model):
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
    return self.postcode

class Client(models.Model):
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



