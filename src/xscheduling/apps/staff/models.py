from django.contrib.auth.models import User
from django.db import models
from django.utils.text import capfirst
from django.utils.translation import ugettext_lazy as _
from client.models import WorkflowmaxBase, Address, ContactBase
from workflowmax.staff.models import Staff as WorkflowmaxStaff

class Skill(models.Model):
# I think we don't need order for types, maybe we need something like short name or abbreviations. 
#  order = models.SmallPositiveIntegerField(_('order'))
  name = models.CharField(_('name'), max_length=255)
  rate = models.DecimalField(_('rate'), max_digits=6, decimal_places=2, default='10.00', help_text=_('hourly rate, ex: 15.99'))

  class Meta:
    ordering = ['name']
    verbose_name = _('skill')
    verbose_name_plural = _('skills')

  def __unicode__(self):
    return self.name

class Staff(WorkflowmaxBase, User):
  salutation = models.CharField(_('salutation'), max_length=3, choices = ContactBase.SALUTATION_LIST, default=ContactBase.MR)
#  name = models.CharField(_('name'), max_length=255)
  address = models.OneToOneField(Address, related_name='staff_address', verbose_name=_('address'), blank=True, null=True)
  phone = models.CharField(_('phone'), max_length=255, null=True, blank=True, help_text=_('(Ex. 020828129)'))
  mobile = models.CharField(_('mobile'), max_length=255, null=True, blank=True, help_text=_('(Ex. 020828129)'))
#  email = models.EmailField(_('email'), null=True, blank=True)
  payrollcode = models.CharField(_('payrollcode'), max_length=255, null=True, blank=True)
  skills = models.ManyToManyField(Skill, related_name='staff', verbose_name=_('skills'))

  class Meta:
    verbose_name = _('staff')
    verbose_name_plural = _('staff')

  def __unicode__(self):
    return self.username

  def save(self, *args, **kwargs):
    if not self.address:
      address = Address()
      address.save()
      self.address = address
    super(Staff, self).save(*args, **kwargs)

  def delete(self):
    super(Staff, self).delete()
    self.address.delete()

  def wm_sync(self):
    if self.username:
      wm_staff = WorkflowmaxStaff()
      if self.wm_id:
        wm_staff.id = int(self.wm_id)
      wm_staff.name = self.username
      wm_staff.address = str(self.address)
      wm_staff.phone = self.phone
      wm_staff.mobile = self.mobile
      wm_staff.email = self.email
      wm_staff.payrollcode = self.payrollcode
      wm_staff = wm_staff.save()
      if not self.wm_id:
        self.wm_id = wm_staff.id
        self.save()

  def wm_delete(self):
    if self.wm_id:
      wm_staff = WorkflowmaxStaff.objects.get(id=self.wm_id)
      wm_staff.delete()

  # we have to include save() here, because of OneToOne field behaviour
  def wm_import(self, wm_staff):
    address = Address()
    address.wm_import(wm_staff.address)
    address.save()
    self.address = address
    self.wm_id = wm_staff.id
    self.username = wm_staff.name
    self.phone = wm_staff.phone
    self.mobile = wm_staff.mobile
    self.email = wm_staff.email
    self.payrollcode = wm_staff.payrollcode
    self.save()
