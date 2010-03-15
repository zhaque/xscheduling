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
from staff.forms import StaffForm
from staff.models import Staff
from workflowmax.staff.models import Staff as WorkflowmaxStaff

def list_staff(request):
  context_vars = dict()
  context_vars['header'] = capfirst(_('staff'))
  context_vars['staff_list'] = Staff.objects.all()
  return direct_to_template(request, template='staff/list.html', extra_context=context_vars)

def import_staff(request):
  context_vars = dict()
  context_vars['header'] = capfirst(_('import staff from workflowmax'))
  context_vars['comment'] = capfirst(_('this will destroy all your local staff, please confirm your decision.'))
  if request.method == "POST":
    for staff in Staff.objects.all():
      staff.delete()
    wm_staff_list = WorkflowmaxStaff.objects.all()
    for wm_staff in wm_staff_list:
      staff = Staff()
      staff.wm_import(wm_staff)
    return HttpResponseRedirect(reverse('staff-list'))
  
  return direct_to_template(request, template='staff/import.html', extra_context=context_vars)

def get_staff(request, object_id):
  context_vars = dict()
  try:
    object_id = int(object_id)
  except ValueError:
    return HttpResponseRedirect(reverse('staff-list'))
  staff = Staff.objects.get(id=object_id)
  context_vars['header'] = capfirst(_('staff %s') % staff.username)
  context_vars['staff'] = staff
  return direct_to_template(request, template='staff/view.html', extra_context=context_vars)

def add_staff(request):
  context_vars = dict()
  context_vars['header'] = capfirst(_('add new staff'))
  staff_form = StaffForm()
  address_form = AddressForm()
  if request.method == "POST":
    staff_form = StaffForm(request.POST, request.FILES)
    address_form = AddressForm(request.POST, request.FILES)
    try:
      if staff_form.is_valid() and address_form.is_valid():
        staff = staff_form.save()
        address_form = AddressForm(request.POST, request.FILES, instance=staff.address)
        if not address_form.is_valid():
          raise InvalidForm()
        address_form.save()
        if settings.WORKFLOWMAX_APIKEY and settings.WORKFLOWMAX_ACCOUNTKEY:
          staff.wm_sync()
        return HttpResponseRedirect(reverse('staff-view', args=[staff.id]))
    except InvalidForm:
      pass
  
  context_vars['staff_form'] = staff_form
  context_vars['address_form'] = address_form
  return direct_to_template(request, template='staff/form.html', extra_context=context_vars)

def edit_staff(request, object_id):
  context_vars = dict()
  try:
    object_id = int(object_id)
    staff = Staff.objects.get(id=object_id)
  except ValueError, ObjectDoesNotExist:
    return HttpResponseRedirect(reverse('staff-list'))
  
  context_vars['header'] = capfirst(_('edit staff %s') % staff.username)
  staff_form = StaffForm(instance=staff)
  address_form = AddressForm(instance=staff.address)
  if request.method == "POST":
    staff_form = StaffForm(request.POST, request.FILES, instance=staff)
    address_form = AddressForm(request.POST, request.FILES, instance=staff.address)
    if staff_form.is_valid() and address_form.is_valid():
      staff = staff_form.save()
      address_form.save()
      if settings.WORKFLOWMAX_APIKEY and settings.WORKFLOWMAX_ACCOUNTKEY:
        staff.wm_sync()
      return HttpResponseRedirect(reverse('staff-view', args=[staff.id]))
  
  context_vars['staff_form'] = staff_form
  context_vars['address_form'] = address_form
  return direct_to_template(request, template='staff/form.html', extra_context=context_vars)

def delete_staff(request, object_id):
  context_vars = dict()
  try:
    object_id = int(object_id)
    staff = Staff.objects.get(id=object_id)
  except ValueError, ObjectDoesNotExist:
    return HttpResponseRedirect(reverse('staff-list'))

  if request.method == 'POST' and settings.WORKFLOWMAX_APIKEY and settings.WORKFLOWMAX_ACCOUNTKEY:
    staff.wm_delete()
  
  return delete_object(request, object_id=staff.id, model=Staff, login_required=True, template_name='staff/delete.html', post_delete_redirect=reverse('staff-list'), extra_context={'header': capfirst(_('delete staff')), 'comment': capfirst(_('you are trying to delete staff "%s". Sure?') % staff.username)})

def get_staff_jobs(request, object_id):
  pass

