from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.text import capfirst
from django.utils.translation import ugettext as _
from django.views.generic.simple import direct_to_template
from client.models import Client
from job.forms import AddJobForm
from staff.models import Staff
from supplier.models import Supplier
from uni_form.helpers import FormHelper, Submit, Reset, Layout, HTML, Row

@login_required
def root(request):
  context_vars = dict()
  context_vars['header'] = capfirst(_('schedule'))

  job_form = AddJobForm()
  helper = FormHelper()
  submit = Submit('save',_('save'))
  helper.add_input(submit)
  layout = Layout(
    Row(HTML('<a href="%s">%s</a>' % (reverse('client-add'), _('new client'))), 'client'),
    'type', 
    'name', 
    'description', 
    'state', 
    'start_date', 
    'due_date', 
    Row(HTML('<a href="%s">%s</a>' % (reverse('staff-add'), _('new staff'))), 'staff'),
    Row(HTML('<a href="%s">%s</a>' % (reverse('supplier-add'), _('new supplier'))), 'suppliers'),
    )
  helper.add_layout(layout)

  context_vars['form'] = job_form
  context_vars['helper'] = helper

  return direct_to_template(request, template='schedule/root.html', extra_context=context_vars)

@login_required
def contacts(request):
  context_vars = dict()
  context_vars['header'] = capfirst(_('contacts'))
  context_vars['clients'] = Client.objects.all()
  context_vars['staff_list'] = Staff.objects.all()
  context_vars['suppliers'] = Supplier.objects.all()
  return direct_to_template(request, template='schedule/contacts.html', extra_context=context_vars)
