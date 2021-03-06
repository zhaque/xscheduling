from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _
from django.utils.text import capfirst
from django.views.generic.create_update import delete_object
from django.views.generic.simple import direct_to_template

from uni_form.helpers import FormHelper, Submit, Reset

from client.forms import ClientForm, ContactForm, AddressForm, InvalidForm
from client.models import Client, Note, Contact, Address
from workflowmax.client.models import Client as WorkflowmaxClient

@login_required
def list_clients(request):
  context_vars = dict()
  context_vars['header'] = capfirst(_('clients'))
  context_vars['clients'] = Client.objects.all()
  return direct_to_template(request, template='client/list.html', extra_context=context_vars)

@login_required
def get_client(request, object_id):
  context_vars = dict()
  try:
    object_id = int(object_id)
  except ValueError:
    return HttpResponseRedirect(reverse('client-list'))
  client = Client.objects.get(id=object_id)
  context_vars['header'] = capfirst(_('client %s') % client.name)
  context_vars['client'] = client
  return direct_to_template(request, template='client/view.html', extra_context=context_vars)

@login_required
def add_client(request):
  return_to = request.GET.get('return_to', '')

  context_vars = dict()
  context_vars['header'] = capfirst(_('add new client'))
  client_form = ClientForm(prefix='client')
#  contact_form = ContactForm(prefix='contact')
  address_form = AddressForm(prefix='address')
  postal_address_form = AddressForm(prefix='post_address')
  if request.method == "POST":
    client_form = ClientForm(request.POST, request.FILES, prefix='client')
    address_form = AddressForm(request.POST, request.FILES, prefix='address')
    postal_address_form = AddressForm(request.POST, request.FILES, prefix='post_address')
    try:
      if client_form.is_valid() and address_form.is_valid():
        client = client_form.save()
        address_form = AddressForm(request.POST, request.FILES, prefix='address', instance=client.address)
        if not address_form.is_valid():
          raise InvalidForm()
        address_form.save()
        postal_address_form = AddressForm(request.POST, request.FILES, prefix='post_address', instance=client.postal_address)
        if postal_address_form.is_valid():
          postal_address_form.save()
        else:
          client.postal_address.postcode = client.address.postcode
          client.postal_address.address = client.address.address
          client.postal_address.city = client.address.city
          client.postal_address.county = client.address.county
          client.postal_address.country = client.address.country
          client.postal_address.latitude = client.address.latitude
          client.postal_address.longitude = client.address.longitude
          client.postal_address.save()
        if settings.WORKFLOWMAX_APIKEY and settings.WORKFLOWMAX_ACCOUNTKEY:
          client.wm_sync()
        if not return_to:
          return_to = reverse('client-view', args=[client.id])
        messages.success(request, capfirst(_('client was created successfully')), fail_silently=True)
        return HttpResponseRedirect(return_to)
    except InvalidForm:
      pass
  
  context_vars['client_form'] = client_form
  context_vars['address_form'] = address_form
  context_vars['postal_address_form'] = postal_address_form
  return direct_to_template(request, template='client/form.html', extra_context=context_vars)

@login_required
def edit_client(request, object_id):
  return_to = request.GET.get('return_to', '')

  context_vars = dict()
  try:
    object_id = int(object_id)
    client = Client.objects.get(id=object_id)
  except ValueError, ObjectDoesNotExist:
    return HttpResponseRedirect(reverse('client-list'))
  
  context_vars['header'] = capfirst(_('edit client %s') % client.name)
  client_form = ClientForm(prefix='client', instance=client)
  address_form = AddressForm(prefix='address', instance=client.address)
  postal_address_form = AddressForm(prefix='post_address', instance=client.postal_address)
  if request.method == "POST":
    client_form = ClientForm(request.POST, request.FILES, prefix='client', instance=client)
    address_form = AddressForm(request.POST, request.FILES, prefix='address', instance=client.address)
    postal_address_form = AddressForm(request.POST, request.FILES, prefix='post_address', instance=client.postal_address)
    if client_form.is_valid() and address_form.is_valid() and postal_address_form.is_valid():
      client = client_form.save()
      address_form.save()
      postal_address_form.save()
      if settings.WORKFLOWMAX_APIKEY and settings.WORKFLOWMAX_ACCOUNTKEY:
        client.wm_sync()
      if not return_to:
        return_to = reverse('client-view', args=[client.id])
      messages.success(request, capfirst(_('client was modified successfully')), fail_silently=True)
      return HttpResponseRedirect(return_to)
  
  context_vars['client_form'] = client_form
  context_vars['address_form'] = address_form
  context_vars['postal_address_form'] = postal_address_form
  return direct_to_template(request, template='client/form.html', extra_context=context_vars)

@login_required
def delete_client(request, object_id):
  context_vars = dict()
  try:
    object_id = int(object_id)
    client = Client.objects.get(id=object_id)
  except ValueError, ObjectDoesNotExist:
    return HttpResponseRedirect(reverse('client-list'))

  if request.method == 'POST' and settings.WORKFLOWMAX_APIKEY and settings.WORKFLOWMAX_ACCOUNTKEY:
    client.wm_delete()
  
  return delete_object(request, object_id=client.id, model=Client, login_required=True, template_name='client/delete.html', post_delete_redirect=reverse('client-list'), extra_context={'header': capfirst(_('delete client')), 'comment': capfirst(_('you are trying to delete client "%s". Sure?') % client.name)})

@login_required
def add_contact(request, object_id):
  context_vars = dict()
  try:
    object_id = int(object_id)
    client = Client.objects.get(id=object_id)
  except ValueError, ObjectDoesNotExist:
    return HttpResponseRedirect(reverse('client-list'))

  form = ContactForm()
  helper = FormHelper()
  submit = Submit('save',_('save'))
  helper.add_input(submit)
  
  if request.method == "POST":
    form = ContactForm(request.POST, request.FILES)
    if form.is_valid():
      contact = form.save(commit=False)
      contact.client = client
      contact.save()
      if settings.WORKFLOWMAX_APIKEY and settings.WORKFLOWMAX_ACCOUNTKEY:
        contact.wm_sync()
      messages.success(request, capfirst(_('contact was added successfully')), fail_silently=True)
      return HttpResponseRedirect(reverse('client-view', args=[client.id]))
  
  context_vars['form'] = form
  context_vars['helper'] = helper
  return direct_to_template(request, template='client/form.html', extra_context=context_vars)  

@login_required
def edit_contact(request, owner_id, object_id):
  context_vars = dict()
  try:
    owner_id = int(owner_id)
    client = Client.objects.get(id=owner_id)
  except ValueError, ObjectDoesNotExist:
    return HttpResponseRedirect(reverse('client-list'))
  try:
    object_id = int(object_id)
    contact = Contact.objects.get(id=object_id)
  except ValueError, ObjectDoesNotExist:
    return HttpResponseRedirect(reverse('client-view', args=[client.id]))

  form = ContactForm(instance=contact)
  helper = FormHelper()
  submit = Submit('save',_('save'))
  helper.add_input(submit)
  
  if request.method == "POST":
    form = ContactForm(request.POST, request.FILES, instance=contact)
    if form.is_valid():
      form.save()
      if settings.WORKFLOWMAX_APIKEY and settings.WORKFLOWMAX_ACCOUNTKEY:
        contact.wm_sync()
      messages.success(request, capfirst(_('contact was modified successfully')), fail_silently=True)
      return HttpResponseRedirect(reverse('client-view', args=[client.id]))
  
  context_vars['form'] = form
  context_vars['helper'] = helper
  return direct_to_template(request, template='client/form.html', extra_context=context_vars)

@login_required
def add_note(request, object_id):
  pass
@login_required
def get_note(request, owner_id, object_id):
  pass
@login_required
def edit_note(request, owner_id, object_id):
  pass

@login_required
def import_clients(request):
  context_vars = dict()
  context_vars['header'] = capfirst(_('import clients from workflowmax'))
  context_vars['comment'] = capfirst(_('this will destroy all your local clients, please confirm your decision.'))
  if request.method == "POST":
    for client in Client.objects.all():
      client.delete()
    wm_clients = WorkflowmaxClient.objects.all()
    for wm_client in wm_clients:
      client = Client()
      client.wm_import(wm_client)
    messages.success(request, capfirst(_('clients were imported successfully')), fail_silently=True)
    return HttpResponseRedirect(reverse('client-list'))
  
  return direct_to_template(request, template='client/import.html', extra_context=context_vars)
  