from django.db import models
from django.utils.translation import ugettext_lazy as _
from client.models import WorkflowmaxBase, ContactBase, ClientBase
from workflowmax.supplier.models import Supplier as WorkflowmaxSupplier, Contact as WorkflowmaxContact

class Contact(ContactBase):
  supplier = models.ForeignKey('Supplier', verbose_name="supplier", related_name='contacts')

  def wm_sync(self):
    if self.name and self.supplier.wm_id:
      wm_contact = WorkflowmaxContact()
      if self.wm_id:
        wm_contact.id = int(self.wm_id)
      else:
        wm_contact.owner_id = int(self.supplier.wm_id)      
      wm_contact.name = self.name
      wm_contact.mobile = self.mobile
      wm_contact.email = self.email
      wm_contact.phone = self.phone
      wm_contact.position = self.position
      wm_contact = wm_contact.save()
      if not self.wm_id:
        self.wm_id = wm_contact.id
        self.save()

class Supplier(ClientBase):
  class Meta:
    verbose_name = _('supplier')
    verbose_name_plural = _('suppliers')

  def wm_sync(self):
    if self.name:
      wm_supplier = WorkflowmaxSupplier()
      if self.wm_id:
        wm_supplier.id = int(self.wm_id)
      wm_supplier.name = self.name
      wm_supplier.address = str(self.address)
      wm_supplier.postal_address = str(self.postal_address)
      wm_supplier.phone = self.phone
      wm_supplier.fax = self.fax
      wm_supplier.website = self.website
      wm_supplier.referral_source = self.referral_source
      wm_supplier = wm_supplier.save()
      if not self.wm_id:
        self.wm_id = wm_supplier.id
        self.save()
      if self.contacts.all():
        for contact in self.contacts.all():
          contact.wm_sync()

  def wm_delete(self):
    if self.wm_id:
      wm_supplier = WorkflowmaxSupplier.objects.get(id=self.wm_id)
      wm_supplier.delete()

  def wm_import_contacts(self, wm_supplier):
    for wm_contact in wm_supplier.contacts:
      contact = Contact()
      contact.supplier = self
      contact.wm_import(wm_contact)
      contact.save()

