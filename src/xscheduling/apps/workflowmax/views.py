from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.text import capfirst
from django.utils.translation import ugettext as _
from django.views.generic.simple import direct_to_template
from workflowmax.models import Client, Contact

def list_clients(request):
  context_vars = dict()
  context_vars['header'] = capfirst(_('client list'))
  context_vars['clients'] = Client.client_objects.all()
  return direct_to_template(request, template='workflowmax/list.html', extra_context=context_vars)

def get_client(request, object_id):
  try:
    object_id = int(object_id)
  except ValueError:
    return HttpResponseRedirect(reverse('workflowmax-list'))
  context_vars = dict()
  context_vars['header'] = '%s %d' % (capfirst(_('client')), object_id)
  context_vars['client'] = Client.objects.get(id=object_id)
  return direct_to_template(request, template='workflowmax/view.html', extra_context=context_vars)

def get_contact(request, object_id):
  try:
    object_id = int(object_id)
  except ValueError:
    return HttpResponseRedirect(reverse('workflowmax-list'))
  context_vars = dict()
  context_vars['header'] = '%s %d' % (capfirst(_('contact')), object_id)
  context_vars['contact'] = Contact.objects.get(id=object_id)
  return direct_to_template(request, template='workflowmax/view.html', extra_context=context_vars)
