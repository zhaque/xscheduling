from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.text import capfirst
from django.utils.translation import ugettext as _
from django.views.generic.simple import direct_to_template
from client.models import Client
from staff.models import Staff
from supplier.models import Supplier

def root(request):
  context_vars = dict()
  context_vars['header'] = capfirst(_('schedule'))
  return direct_to_template(request, template='schedule/root.html', extra_context=context_vars)

@login_required
def contacts(request):
  context_vars = dict()
  context_vars['header'] = capfirst(_('contacts'))
  context_vars['clients'] = Client.objects.all()
  context_vars['staff_list'] = Staff.objects.all()
  context_vars['suppliers'] = Supplier.objects.all()
  return direct_to_template(request, template='schedule/contacts.html', extra_context=context_vars)
