from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _
from django.utils.text import capfirst
from django.views.generic.create_update import delete_object
from django.views.generic.simple import direct_to_template

from uni_form.helpers import FormHelper, Submit, Reset

from client.forms import AddressForm, InvalidForm
from client.models import Address
from supplier.forms import SupplierForm, ContactForm
from supplier.models import Supplier, Contact
from workflowmax.supplier.models import Supplier as WorkflowmaxSupplier

def list_suppliers(request):
  context_vars = dict()
  context_vars['header'] = capfirst(_('suppliers'))
  context_vars['suppliers'] = Supplier.objects.all()
  return direct_to_template(request, template='supplier/list.html', extra_context=context_vars)

def get_supplier(request, object_id):
  context_vars = dict()
  try:
    object_id = int(object_id)
  except ValueError:
    return HttpResponseRedirect(reverse('supplier-list'))
  supplier = Supplier.objects.get(id=object_id)
  context_vars['header'] = capfirst(_('supplier %s') % supplier.name)
  context_vars['supplier'] = supplier
  return direct_to_template(request, template='supplier/view.html', extra_context=context_vars)

def add_supplier(request):
  context_vars = dict()
  context_vars['header'] = capfirst(_('add new supplier'))
  supplier_form = SupplierForm()
  address_form = AddressForm(prefix='address')
  postal_address_form = AddressForm(prefix='post_address')
  if request.method == "POST":
    supplier_form = SupplierForm(request.POST, request.FILES)
    address_form = AddressForm(request.POST, request.FILES, prefix='address')
    postal_address_form = AddressForm(request.POST, request.FILES, prefix='post_address')
    try:
      if supplier_form.is_valid() and address_form.is_valid() and postal_address_form.is_valid():
        supplier = supplier_form.save()
        address_form = AddressForm(request.POST, request.FILES, prefix='address', instance=supplier.address)
        if not address_form.is_valid():
          raise InvalidForm()
        address_form.save()
        postal_address_form = AddressForm(request.POST, request.FILES, prefix='post_address', instance=supplier.postal_address)
        if not postal_address_form.is_valid():
          raise InvalidForm()
        postal_address_form.save()
        if settings.WORKFLOWMAX_APIKEY and settings.WORKFLOWMAX_ACCOUNTKEY:
          supplier.wm_sync()
        return HttpResponseRedirect(reverse('supplier-view', args=[supplier.id]))
    except InvalidForm:
      pass
  
  context_vars['supplier_form'] = supplier_form
  context_vars['address_form'] = address_form
  context_vars['postal_address_form'] = postal_address_form
  return direct_to_template(request, template='supplier/form.html', extra_context=context_vars)

def edit_supplier(request, object_id):
  context_vars = dict()
  try:
    object_id = int(object_id)
    supplier = Supplier.objects.get(id=object_id)
  except ValueError, ObjectDoesNotExist:
    return HttpResponseRedirect(reverse('supplier-list'))
  
  context_vars['header'] = capfirst(_('edit supplier %s') % supplier.name)
  supplier_form = SupplierForm(instance=supplier)
  address_form = AddressForm(prefix='address', instance=supplier.address)
  postal_address_form = AddressForm(prefix='post_address', instance=supplier.postal_address)
  if request.method == "POST":
    supplier_form = SupplierForm(request.POST, request.FILES, instance=supplier)
    address_form = AddressForm(request.POST, request.FILES, prefix='address', instance=supplier.address)
    postal_address_form = AddressForm(request.POST, request.FILES, prefix='post_address', instance=supplier.postal_address)
    if supplier_form.is_valid() and address_form.is_valid() and postal_address_form.is_valid():
      supplier = supplier_form.save()
      address_form.save()
      postal_address_form.save()
      if settings.WORKFLOWMAX_APIKEY and settings.WORKFLOWMAX_ACCOUNTKEY:
        supplier.wm_sync()
      return HttpResponseRedirect(reverse('supplier-view', args=[supplier.id]))
  
  context_vars['supplier_form'] = supplier_form
  context_vars['address_form'] = address_form
  context_vars['postal_address_form'] = postal_address_form
  return direct_to_template(request, template='supplier/form.html', extra_context=context_vars)

def delete_supplier(request, object_id):
  context_vars = dict()
  try:
    object_id = int(object_id)
    supplier = Supplier.objects.get(id=object_id)
  except ValueError, ObjectDoesNotExist:
    return HttpResponseRedirect(reverse('supplier-list'))

  if settings.WORKFLOWMAX_APIKEY and settings.WORKFLOWMAX_ACCOUNTKEY:
    supplier.wm_delete()
  
  return delete_object(request, object_id=supplier.id, model=Supplier, login_required=True, template_name='supplier/delete.html', post_delete_redirect=reverse('supplier-list'), extra_context={'header': capfirst(_('delete supplier')), 'comment': capfirst(_('you are trying to delete supplier "%s". Sure?') % supplier.name)})

def add_contact(request, object_id):
  context_vars = dict()
  try:
    object_id = int(object_id)
    supplier = Supplier.objects.get(id=object_id)
  except ValueError, ObjectDoesNotExist:
    return HttpResponseRedirect(reverse('supplier-list'))

  form = ContactForm()
  helper = FormHelper()
  helper.form_class = 'uniform'
  submit = Submit('save',_('save'))
  helper.add_input(submit)
  
  if request.method == "POST":
    form = ContactForm(request.POST, request.FILES)
    if form.is_valid():
      contact = form.save(commit=False)
      contact.supplier = supplier
      contact.save()
      if settings.WORKFLOWMAX_APIKEY and settings.WORKFLOWMAX_ACCOUNTKEY:
        contact.wm_sync()
      return HttpResponseRedirect(reverse('supplier-view', args=[supplier.id]))
  
  context_vars['form'] = form
  context_vars['helper'] = helper
  return direct_to_template(request, template='supplier/uniform.html', extra_context=context_vars)

def edit_contact(request, owner_id, object_id):
  context_vars = dict()
  try:
    owner_id = int(owner_id)
    supplier = Supplier.objects.get(id=owner_id)
  except ValueError, ObjectDoesNotExist:
    return HttpResponseRedirect(reverse('supplier-list'))
  try:
    object_id = int(object_id)
    contact = Contact.objects.get(id=object_id)
  except ValueError, ObjectDoesNotExist:
    return HttpResponseRedirect(reverse('supplier-view', args=[supplier.id]))

  form = ContactForm(instance=contact)
  helper = FormHelper()
  helper.form_class = 'uniform'
  submit = Submit('save',_('save'))
  helper.add_input(submit)
  
  if request.method == "POST":
    form = ContactForm(request.POST, request.FILES, instance=contact)
    if form.is_valid():
      form.save()
      if settings.WORKFLOWMAX_APIKEY and settings.WORKFLOWMAX_ACCOUNTKEY:
        contact.wm_sync()
      return HttpResponseRedirect(reverse('supplier-view', args=[supplier.id]))
  
  context_vars['form'] = form
  context_vars['helper'] = helper
  return direct_to_template(request, template='supplier/uniform.html', extra_context=context_vars)

def import_suppliers(request):
  context_vars = dict()
  context_vars['header'] = capfirst(_('import suppliers from workflowmax'))
  context_vars['comment'] = capfirst(_('this will destroy all your local suppliers, please confirm your decision.'))
  if request.method == "POST":
    for supplier in Supplier.objects.all():
      supplier.delete()
    wm_suppliers = WorkflowmaxSupplier.objects.all()
    for wm_supplier in wm_suppliers:
      supplier = Supplier()
      supplier.wm_import(wm_supplier)
    return HttpResponseRedirect(reverse('supplier-list'))
  
  return direct_to_template(request, template='supplier/import.html', extra_context=context_vars)
  