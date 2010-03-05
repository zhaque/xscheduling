from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _
from django.utils.text import capfirst
from django.views.generic.simple import direct_to_template

from uni_form.helpers import FormHelper, Submit, Reset

from client.forms import ClientForm, ContactForm, AddressForm, InvalidForm
from client.models import Client, Note, Contact, Address

def list_clients(request):
  context_vars = dict()
  context_vars['header'] = capfirst(_('clients'))
  context_vars['clients'] = Client.objects.all()
  return direct_to_template(request, template='client/list.html', extra_context=context_vars)

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

def add_client(request):
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
      if client_form.is_valid() and address_form.is_valid() and postal_address_form.is_valid():
        client = client_form.save()
        address_form = AddressForm(request.POST, request.FILES, prefix='address', instance=client.address)
        if not address_form.is_valid():
          raise InvalidForm()
        address_form.save()
        postal_address_form = AddressForm(request.POST, request.FILES, prefix='post_address', instance=client.postal_address)
        if not postal_address_form.is_valid():
          raise InvalidForm()
        postal_address_form.save()
        return HttpResponseRedirect(reverse('client-view', args=[client.id]))
    except InvalidForm:
      pass
  
  context_vars['client_form'] = client_form
  context_vars['address_form'] = address_form
  context_vars['postal_address_form'] = postal_address_form
  return direct_to_template(request, template='client/form.html', extra_context=context_vars)

def edit_client(request, object_id):
  context_vars = dict()
  try:
    object_id = int(object_id)
  except ValueError:
    return HttpResponseRedirect(reverse('client-list'))
  
  client = Client.objects.get(id=object_id)
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
      return HttpResponseRedirect(reverse('client-view', args=[client.id]))
  
  context_vars['client_form'] = client_form
  context_vars['address_form'] = address_form
  context_vars['postal_address_form'] = postal_address_form
  return direct_to_template(request, template='client/form.html', extra_context=context_vars)

def add_contact(request, object_id):
  pass
def get_contact(request, owner_id, object_id):
  pass
def edit_contact(request, owner_id, object_id):
  pass
def add_note(request, object_id):
  pass
def get_note(request, owner_id, object_id):
  pass
def edit_note(request, owner_id, object_id):
  pass
