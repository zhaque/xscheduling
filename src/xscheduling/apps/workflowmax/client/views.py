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

# Client views
@login_required
def list_clients(request):
  context_vars = dict()
  context_vars['header'] = capfirst(_('client list'))
  context_vars['clients'] = Client.objects.all()
  return direct_to_template(request, template='workflowmax/list.html', extra_context=context_vars)

@login_required
def get_client(request, object_id):
  try:
    object_id = int(object_id)
  except ValueError:
    return HttpResponseRedirect(reverse('workflowmax-client-list'))
  context_vars = dict()
  context_vars['header'] = '%s %d' % (capfirst(_('client')), object_id)
  context_vars['client'] = Client.objects.get(id=object_id)
  return direct_to_template(request, template='workflowmax/view.html', extra_context=context_vars)

@login_required
def edit_client(request, object_id):
  try:
    object_id = int(object_id)
  except ValueError:
    return HttpResponseRedirect(reverse('workflowmax-client-list'))
  context_vars = dict()
  context_vars['header'] = '%s %d' % (capfirst(_('client')), object_id)
  client = Client.objects.get(id=object_id)
  form = ClientForm(client.to_dict())
  helper = FormHelper()
  helper.form_class = 'uniform'
  submit = Submit('save',_('save'))
  helper.add_input(submit)
  if request.method == "POST":
    form = ClientForm(request.POST, request.FILES)
    if form.is_valid():
      client.name = form.cleaned_data['name']
      client.address = form.cleaned_data['address']
      client.postal_address = form.cleaned_data['postal_address']
      client.phone = form.cleaned_data['phone']
      client.fax = form.cleaned_data['fax']
      client.website = form.cleaned_data['website']
      client.referral_source = form.cleaned_data['referral_source']
      client.save()
      return HttpResponseRedirect(reverse('workflowmax-client', args=[client.id]))
  
  context_vars['form'] = form
  context_vars['helper'] = helper
  return direct_to_template(request, template='workflowmax/form.html', extra_context=context_vars)

@login_required
def add_client(request):
  context_vars = dict()
  context_vars['header'] = capfirst(_('add new client'))
  form = ClientForm()
  helper = FormHelper()
  helper.form_class = 'uniform'
  submit = Submit('save',_('save'))
  helper.add_input(submit)
  if request.method == "POST":
    form = ClientForm(request.POST, request.FILES)
    if form.is_valid():
      client = Client()
      client.name = form.cleaned_data['name']
      client.address = form.cleaned_data['address']
      client.postal_address = form.cleaned_data['postal_address']
      client.phone = form.cleaned_data['phone']
      client.fax = form.cleaned_data['fax']
      client.website = form.cleaned_data['website']
      client.referral_source = form.cleaned_data['referral_source']
      client = client.save()
      return HttpResponseRedirect(reverse('workflowmax-client', args=[client.id]))
  
  context_vars['form'] = form
  context_vars['helper'] = helper
  return direct_to_template(request, template='workflowmax/form.html', extra_context=context_vars)

@login_required
def delete_client(request, object_id):
  try:
    object_id = int(object_id)
  except ValueError:
    return HttpResponseRedirect(reverse('workflowmax-client-list'))
  context_vars = dict()
  context_vars['header'] = '%s %d' % (capfirst(_('delete client')), object_id)
  context_vars['comment'] = _('You are trying to delete client "%d". Sure?') % object_id
  client = Client.objects.get(id=object_id)
  
  if request.method == "POST":
    client.delete()
    return HttpResponseRedirect(reverse('workflowmax-client-list'))

  return direct_to_template(request, template='workflowmax/delete.html', extra_context=context_vars)

@login_required
def add_client_contact(request, object_id):
  try:
    object_id = int(object_id)
  except ValueError:
    return HttpResponseRedirect(reverse('workflowmax-client-list'))
  context_vars = dict()
  context_vars['header'] = capfirst(_('add new contact for client %d') % object_id)
  form = ContactForm()
  helper = FormHelper()
  helper.form_class = 'uniform'
  submit = Submit('save',_('save'))
  helper.add_input(submit)
  if request.method == "POST":
    form = ContactForm(request.POST, request.FILES)
    if form.is_valid():
      contact = Contact()
      contact.owner_id = object_id
      contact.name = form.cleaned_data['name']
      contact.mobile = form.cleaned_data['mobile']
      contact.email = form.cleaned_data['email']
      contact.phone = form.cleaned_data['phone']
      contact.position = form.cleaned_data['position']
      contact = contact.save()
      return HttpResponseRedirect(reverse('workflowmax-client', args=[object_id]))
  
  context_vars['form'] = form
  context_vars['helper'] = helper
  return direct_to_template(request, template='workflowmax/form.html', extra_context=context_vars)

@login_required
def edit_client_contact(request, owner_id, object_id):
  try:
    owner_id = int(owner_id)
  except ValueError:
    return HttpResponseRedirect(reverse('workflowmax-client-list'))
  try:
    object_id = int(object_id)
  except ValueError:
    return HttpResponseRedirect(reverse('workflowmax-client', args=[owner_id]))
  context_vars = dict()
  context_vars['header'] = capfirst(_('edit contact %d') % object_id)
  contact = Contact.objects.get(id=object_id)
  form = ContactForm(contact.to_dict())
  helper = FormHelper()
  helper.form_class = 'uniform'
  submit = Submit('save',_('save'))
  helper.add_input(submit)
  if request.method == "POST":
    form = ContactForm(request.POST, request.FILES)
    if form.is_valid():
      contact.name = form.cleaned_data['name']
      contact.mobile = form.cleaned_data['mobile']
      contact.email = form.cleaned_data['email']
      contact.phone = form.cleaned_data['phone']
      contact.position = form.cleaned_data['position']
      contact.save()
      return HttpResponseRedirect(reverse('workflowmax-client', args=[owner_id]))
  
  context_vars['form'] = form
  context_vars['helper'] = helper
  return direct_to_template(request, template='workflowmax/form.html', extra_context=context_vars)

