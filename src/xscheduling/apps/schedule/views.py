from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.text import capfirst
from django.utils.translation import ugettext as _
from django.views.generic.simple import direct_to_template
from client.forms import ClientForm, AddressForm
from client.models import Client
from job.forms import RootPageAddJobForm, EditJobForm
from staff.models import Staff
from supplier.models import Supplier
from uni_form.helpers import FormHelper, Submit, Reset, Layout, HTML, Row, Hidden

@login_required
def root(request):
  context_vars = dict()
  context_vars['header'] = capfirst(_('schedule'))
  
  job_form = RootPageAddJobForm()
  helper = FormHelper()
  helper.set_form_action(reverse('job-add'))
  submit = Submit('save',_('save'))
  helper.add_input(submit)
  layout = Layout( 
    HTML('<h3>%s</h3>' % capfirst(_('job details'))),
    'description', 'type',
    HTML('<h3>%s</h3>' % capfirst(_('time and staff'))),
    'start_date', 'due_date', 'staff'
    )
  helper.add_layout(layout)

  client_query = request.GET.get('q', '')
  if client_query:
    clients = Client.objects.search(client_query)
    if clients:
      if len(clients) == 1:
        context_vars['client'] = clients[0]
        try:
          job = clients[0].jobs.latest()
          context_vars['job_edit_form'] = EditJobForm(instance=job)
          editjob_helper = FormHelper()
          editjob_helper.set_form_action(reverse('job-edit', args=[job.id]))
          submit = Submit('save',_('save'))
          editjob_helper.add_input(submit)
          recomended_staff_html = ''
          for s in ['%s, ' % staff for staff in job.get_valid_staff()]: recomended_staff_html +=s
          layout = Layout( 
            'state', 
            Row(HTML('<span style="color:red">Recommended: %s</span>' % recomended_staff_html), HTML('<a href="%s">%s</a>' % (reverse('staff-add'), _('add new'))), 'staff'),
            Row(HTML('<a href="%s">%s</a>' % (reverse('supplier-add'), _('add new'))), 'suppliers'),
            )
          editjob_helper.add_layout(layout)
          context_vars['edit_job_helper'] = editjob_helper

        except ObjectDoesNotExist:
          context_vars['job_form'] = job_form
          client_input = Hidden('client', clients[0].id)
          helper.add_input(client_input)
          context_vars['helper'] = helper
      else:
        context_vars['clients'] = clients
    else:
      context_vars['client_form'] = ClientForm(prefix='client')
      context_vars['address_form'] = AddressForm(prefix='address')
      context_vars['job_form'] = job_form
      context_vars['helper'] = helper

  context_vars['staff_list'] = Staff.objects.all()
  

#  job_form = RootPageAddJobForm()
#  helper = FormHelper()
#  helper.set_form_action(reverse('job-add'))
#  submit = Submit('save',_('save'))
#  helper.add_input(submit)
#  layout = Layout(
#    Row(HTML('<a href="%s">%s</a>' % (reverse('client-add'), _('new client'))), 'client'),
#    'type', 
#    'name', 
#    'description', 
##    'state', 
#    'start_date', 
#    'due_date', 
#    'staff',
##    Row(HTML('<a href="%s">%s</a>' % (reverse('staff-add'), _('new staff'))), 'staff'),
##    Row(HTML('<a href="%s">%s</a>' % (reverse('supplier-add'), _('new supplier'))), 'suppliers'),
#    )
#  helper.add_layout(layout)
#
#  context_vars['form'] = job_form
#  context_vars['helper'] = helper

  return direct_to_template(request, template='schedule/root.html', extra_context=context_vars)

@login_required
def contacts(request):
  context_vars = dict()
  context_vars['header'] = capfirst(_('contacts'))
  context_vars['clients'] = Client.objects.all()
  context_vars['staff_list'] = Staff.objects.all()
  context_vars['suppliers'] = Supplier.objects.all()
  return direct_to_template(request, template='schedule/contacts.html', extra_context=context_vars)
