from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.text import capfirst
from django.utils.translation import ugettext as _
from django.views.generic.simple import direct_to_template
from client.models import Client
from schedule.forms import ClientForm as RootPageClientForm, AddressForm as RootPageAddressForm, AddJobForm as RootPageAddJobForm, EditJobForm as RootPageEditJobForm
from staff.models import Staff
from supplier.models import Supplier
from uni_form.helpers import FormHelper, Submit, Reset, Layout, HTML, Row, Hidden

@login_required
def root(request, client_name=None, client_id=None, add_job=False):
  client_query = request.GET.get('q', '')
  if client_query:
    return HttpResponseRedirect(reverse('schedule-client', args=[client_query,]))

  context_vars = dict()
  context_vars['header'] = capfirst(_('schedule'))
  
  try:
    staff = Staff.objects.get(user_ptr=request.user)
    context_vars['staff'] = staff
  except ObjectDoesNotExist:
    staff = None

  client = None
  if client_id:
    try:
      client = Client.objects.get(id=client_id)
    except ObjectDoesNotExist:
      return HttpResponseRedirect(reverse('schedule-root'))
    
  if client_name:
    clients = Client.objects.search(client_name)
    if clients:
      if len(clients) == 1:
        client = clients[0]
      else:
        context_vars['clients'] = clients
    else:
      context_vars['client_form'] = RootPageClientForm(prefix='client')
      context_vars['address_form'] = RootPageAddressForm(prefix='address')

  if client:
    context_vars['client'] = client
    try:
      job = client.jobs.latest()
    except ObjectDoesNotExist:
      add_job = True
    if add_job:
      job_form = RootPageAddJobForm()
      helper = FormHelper()
      helper.set_form_action('%s?return_to=%s' % (reverse('job-add'), reverse('schedule-client-byid', args=[client.id,])))
      submit = Submit('save',_('save'))
      helper.add_input(submit)
      layout = Layout( 
        HTML('<h3>%s</h3>' % capfirst(_('job details'))),
        'description', 'type',
        HTML('<h3>%s</h3>' % capfirst(_('time and staff'))),
        'start_date', 'due_date', 'staff'
        )
      helper.add_layout(layout)

      context_vars['job_form'] = job_form
      client_input = Hidden('client', client.id)
      helper.add_input(client_input)
      context_vars['helper'] = helper
    else:                
      context_vars['job_edit_form'] = RootPageEditJobForm(instance=job)
      editjob_helper = FormHelper()
      editjob_helper.set_form_action('%s?return_to=%s' % (reverse('job-edit', args=[job.id]), reverse('schedule-client-byid', args=[client.id,])))
      submit = Submit('save',_('save'))
      editjob_helper.add_input(submit)
      recomended_staff_html = ''
      for s in ['%s, ' % staff for staff in job.get_valid_staff()]: recomended_staff_html +=s
      layout = Layout( 
        'state', 
        Row(HTML('<span style="color:red">Recommended: %s</span>' % recomended_staff_html), HTML('<a href="%s">%s</a>' % (reverse('staff-add'), _('add new'))), 'staff'),
        )
      editjob_helper.add_layout(layout)
      context_vars['edit_job_helper'] = editjob_helper
        
  context_vars['staff_list'] = Staff.objects.all()
  return direct_to_template(request, template='schedule/root.html', extra_context=context_vars)

@login_required
def client_edit(request, client_id):
  client_query = request.GET.get('q', '')
  if client_query:
    return HttpResponseRedirect(reverse('schedule-client', args=[client_query,]))

  context_vars = dict()
  context_vars['header'] = capfirst(_('schedule'))
  
  try:
    client = Client.objects.get(id=client_id)
    context_vars['client_form'] = RootPageClientForm(prefix='client', instance=client)
    context_vars['address_form'] = RootPageAddressForm(prefix='address', instance=client.address)

    if request.method == "POST":
      client_form = RootPageClientForm(request.POST, prefix='client', instance=client)
      address_form = RootPageAddressForm(request.POST, prefix='address', instance=client.address)
      if client_form.is_valid() and address_form.is_valid():
        client = client_form.save()
        address_form.save()
        if settings.WORKFLOWMAX_APIKEY and settings.WORKFLOWMAX_ACCOUNTKEY:
          client.wm_sync()
        return HttpResponseRedirect(reverse('schedule-client-byid', args=[client.id]))
  except ObjectDoesNotExist:
    return HttpResponseRedirect(reverse('schedule-client', args=[client_name,]))      

  context_vars['staff_list'] = Staff.objects.all()
  return direct_to_template(request, template='schedule/root.html', extra_context=context_vars)

@login_required
def contacts(request):
  context_vars = dict()
  context_vars['header'] = capfirst(_('contacts'))
  context_vars['clients'] = Client.objects.all()
  context_vars['staff_list'] = Staff.objects.all()
  context_vars['suppliers'] = Supplier.objects.all()
  return direct_to_template(request, template='schedule/contacts.html', extra_context=context_vars)
