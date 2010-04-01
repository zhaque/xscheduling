from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.text import capfirst
from django.utils.translation import ugettext as _
from django.views.generic.simple import direct_to_template
from uni_form.helpers import FormHelper, Submit, Reset
from workflowmax.client.models import Client, Contact
from workflowmax.client.forms import ClientForm, ContactForm
from workflowmax.exceptions import ResponseStatusError
from workflowmax.job.models import Job, Note, Task
from workflowmax.job.forms import AddJobForm, EditJobForm, NoteForm, TaskForm
from workflowmax.staff.models import Staff
from workflowmax.staff.forms import StaffForm
from workflowmax.supplier.models import Supplier, Contact as SupplierContact
from workflowmax.supplier.forms import SupplierForm

try:
  from xml.etree import ElementTree # for Python 2.5 users
except ImportError:
  from elementtree import ElementTree
import gdata.calendar.service
import gdata.service
import atom.service
import gdata.calendar
import atom
import atom.token_store
import atom.http_interface
import getopt
import sys
import string
import time
from datetime import datetime

# Staff views

@login_required
def list_staff(request):
  context_vars = dict()
  context_vars['header'] = capfirst(_('staff list'))
  context_vars['staff_list'] = Staff.objects.all()
  return direct_to_template(request, template='workflowmax/list.html', extra_context=context_vars)

@login_required
def get_staff(request, object_id):
  try:
    object_id = int(object_id)
  except ValueError:
    return HttpResponseRedirect(reverse('workflowmax-staff-list'))
  context_vars = dict()
  context_vars['header'] = '%s %d' % (capfirst(_('staff')), object_id)
  context_vars['staff'] = Staff.objects.get(id=object_id)
  return direct_to_template(request, template='workflowmax/view.html', extra_context=context_vars)

@login_required
def edit_staff(request, object_id):
  try:
    object_id = int(object_id)
  except ValueError:
    return HttpResponseRedirect(reverse('workflowmax-staff-list'))
  context_vars = dict()
  context_vars['header'] = capfirst(_('edit staff %d') % object_id)
  staff = Staff.objects.get(id=object_id)
  form = StaffForm(staff.to_dict())
  helper = FormHelper()
  helper.form_class = 'uniform'
  submit = Submit('save',_('save'))
  helper.add_input(submit)
  if request.method == "POST":
    form = StaffForm(request.POST, request.FILES)
    if form.is_valid():
      staff.name = form.cleaned_data['name']
      staff.address = form.cleaned_data['address']
      staff.phone = form.cleaned_data['phone']
      staff.mobile = form.cleaned_data['mobile']
      staff.email = form.cleaned_data['email']
      staff.payrollcode = form.cleaned_data['payrollcode']
      staff.save()
      return HttpResponseRedirect(reverse('workflowmax-staff', args=[staff.id]))
  
  context_vars['form'] = form
  context_vars['helper'] = helper
  return direct_to_template(request, template='workflowmax/form.html', extra_context=context_vars)

@login_required
def add_staff(request):
  context_vars = dict()
  context_vars['header'] = capfirst(_('add new staff'))
  form = StaffForm()
  helper = FormHelper()
  helper.form_class = 'uniform'
  submit = Submit('save',_('save'))
  helper.add_input(submit)
  if request.method == "POST":
    form = StaffForm(request.POST, request.FILES)
    if form.is_valid():
      staff = Staff()
      staff.name = form.cleaned_data['name']
      staff.address = form.cleaned_data['address']
      staff.phone = form.cleaned_data['phone']
      staff.mobile = form.cleaned_data['mobile']
      staff.email = form.cleaned_data['email']
      staff.payrollcode = form.cleaned_data['payrollcode']
      staff = staff.save()
      return HttpResponseRedirect(reverse('workflowmax-staff', args=[staff.id]))
  
  context_vars['form'] = form
  context_vars['helper'] = helper
  return direct_to_template(request, template='workflowmax/form.html', extra_context=context_vars)

@login_required
def delete_staff(request, object_id):
  try:
    object_id = int(object_id)
  except ValueError:
    return HttpResponseRedirect(reverse('workflowmax-staff-list'))
  context_vars = dict()
  context_vars['header'] = '%s %d' % (capfirst(_('delete staff')), object_id)
  context_vars['comment'] = _('You are trying to delete staff "%d". Sure?') % object_id
  staff = Staff.objects.get(id=object_id)
  
  if request.method == "POST":
    staff.delete()
    return HttpResponseRedirect(reverse('workflowmax-staff-list'))

  return direct_to_template(request, template='workflowmax/delete.html', extra_context=context_vars)

@login_required
def get_staff_jobs(request, object_id):
  try:
    object_id = int(object_id)
  except ValueError:
    return HttpResponseRedirect(reverse('workflowmax-staff-list'))
  context_vars = dict()
  context_vars['header'] = '%s %d' % (capfirst(_('job list for staff')), object_id)
  staff = Staff.objects.get(id=object_id)
  context_vars['staff'] = staff
  context_vars['jobs'] = Job.objects.filter(staff=staff)
  return direct_to_template(request, template='workflowmax/list.html', extra_context=context_vars)

