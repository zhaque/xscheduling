from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.text import capfirst
from django.utils.translation import ugettext as _
from django.views.generic.simple import direct_to_template
from uni_form.helpers import FormHelper, Submit, Reset
from workflowmax.client.models import Client, Contact
from workflowmax.client.forms import ClientForm, ContactForm
from workflowmax.staff.models import Staff
from workflowmax.staff.forms import StaffForm

def root(request):
  return direct_to_template(request, template='schedule/root.html')
# Client views

def list_clients(request):
  context_vars = dict()
  context_vars['header'] = capfirst(_('client list'))
  context_vars['clients'] = Client.objects.all()
  return direct_to_template(request, template='schedule/list.html', extra_context=context_vars)

def get_client(request, object_id):
  try:
    object_id = int(object_id)
  except ValueError:
    return HttpResponseRedirect(reverse('schedule-client-list'))
  context_vars = dict()
  context_vars['header'] = '%s %d' % (capfirst(_('client')), object_id)
  context_vars['client'] = Client.objects.get(id=object_id)
  return direct_to_template(request, template='schedule/view.html', extra_context=context_vars)

def get_contact(request, object_id):
  try:
    object_id = int(object_id)
  except ValueError:
    return HttpResponseRedirect(reverse('schedule-client-list'))
  context_vars = dict()
  context_vars['header'] = '%s %d' % (capfirst(_('contact')), object_id)
  context_vars['contact'] = Contact.objects.get(id=object_id)
  return direct_to_template(request, template='schedule/view.html', extra_context=context_vars)

def edit_client(request, object_id):
  try:
    object_id = int(object_id)
  except ValueError:
    return HttpResponseRedirect(reverse('schedule-client-list'))
  context_vars = dict()
  context_vars['header'] = '%s %d' % (capfirst(_('client')), object_id)
  client = Client.objects.get(id=object_id)
  form = ClientForm(client.to_dict())
  helper = FormHelper()
  helper.form_class = 'uniform'
  submit = Submit('save',_('save'))
  helper.add_input(submit)
  context_vars['form'] = form
  context_vars['helper'] = helper
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
      return HttpResponseRedirect(reverse('schedule-client', args=[client.id]))
  
  return direct_to_template(request, template='schedule/form.html', extra_context=context_vars)

def add_client(request):
  context_vars = dict()
  context_vars['header'] = capfirst(_('add new client'))
  form = ClientForm()
  helper = FormHelper()
  helper.form_class = 'uniform'
  submit = Submit('save',_('save'))
  helper.add_input(submit)
  context_vars['form'] = form
  context_vars['helper'] = helper
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
      return HttpResponseRedirect(reverse('schedule-client', args=[client.id]))
  
  return direct_to_template(request, template='schedule/form.html', extra_context=context_vars)

def add_contact(request, object_id):
  try:
    object_id = int(object_id)
  except ValueError:
    return HttpResponseRedirect(reverse('schedule-client-list'))
  context_vars = dict()
  context_vars['header'] = capfirst(_('add new contact for client %d') % object_id)
  form = ContactForm()
  helper = FormHelper()
  helper.form_class = 'uniform'
  submit = Submit('save',_('save'))
  helper.add_input(submit)
  context_vars['form'] = form
  context_vars['helper'] = helper
  if request.method == "POST":
    form = ContactForm(request.POST, request.FILES)
    if form.is_valid():
      contact = Contact()
      contact.client_id = object_id
      contact.name = form.cleaned_data['name']
      contact.mobile = form.cleaned_data['mobile']
      contact.email = form.cleaned_data['email']
      contact.phone = form.cleaned_data['phone']
      contact.position = form.cleaned_data['position']
      contact = contact.save()
      return HttpResponseRedirect(reverse('schedule-client', args=[object_id]))
  
  return direct_to_template(request, template='schedule/form.html', extra_context=context_vars)

def edit_contact(request, object_id):
  try:
    object_id = int(object_id)
  except ValueError:
    return HttpResponseRedirect(reverse('schedule-client-list'))
  context_vars = dict()
  context_vars['header'] = capfirst(_('edit contact %d') % object_id)
  contact = Contact.objects.get(id=object_id)
  form = ContactForm(contact.to_dict())
  helper = FormHelper()
  helper.form_class = 'uniform'
  submit = Submit('save',_('save'))
  helper.add_input(submit)
  context_vars['form'] = form
  context_vars['helper'] = helper
  if request.method == "POST":
    form = ContactForm(request.POST, request.FILES)
    if form.is_valid():
      contact.name = form.cleaned_data['name']
      contact.mobile = form.cleaned_data['mobile']
      contact.email = form.cleaned_data['email']
      contact.phone = form.cleaned_data['phone']
      contact.position = form.cleaned_data['position']
      contact.save()
      return HttpResponseRedirect(reverse('schedule-contact', args=[contact.id]))
  
  return direct_to_template(request, template='schedule/form.html', extra_context=context_vars)

# Staff views

def list_staff(request):
  context_vars = dict()
  context_vars['header'] = capfirst(_('staff list'))
  context_vars['staff_list'] = Staff.objects.all()
  return direct_to_template(request, template='schedule/list.html', extra_context=context_vars)

def get_staff(request, object_id):
  try:
    object_id = int(object_id)
  except ValueError:
    return HttpResponseRedirect(reverse('schedule-staff-list'))
  context_vars = dict()
  context_vars['header'] = '%s %d' % (capfirst(_('staff')), object_id)
  context_vars['staff'] = Staff.objects.get(id=object_id)
  return direct_to_template(request, template='schedule/view.html', extra_context=context_vars)

def edit_staff(request, object_id):
  try:
    object_id = int(object_id)
  except ValueError:
    return HttpResponseRedirect(reverse('schedule-staff-list'))
  context_vars = dict()
  context_vars['header'] = capfirst(_('edit staff %d') % object_id)
  staff = Staff.objects.get(id=object_id)
  form = StaffForm(staff.to_dict())
  helper = FormHelper()
  helper.form_class = 'uniform'
  submit = Submit('save',_('save'))
  helper.add_input(submit)
  context_vars['form'] = form
  context_vars['helper'] = helper
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
      return HttpResponseRedirect(reverse('schedule-staff', args=[staff.id]))
  
  return direct_to_template(request, template='schedule/form.html', extra_context=context_vars)

def add_staff(request):
  context_vars = dict()
  context_vars['header'] = capfirst(_('add new staff'))
  form = StaffForm()
  helper = FormHelper()
  helper.form_class = 'uniform'
  submit = Submit('save',_('save'))
  helper.add_input(submit)
  context_vars['form'] = form
  context_vars['helper'] = helper
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
      return HttpResponseRedirect(reverse('schedule-staff', args=[staff.id]))
  
  return direct_to_template(request, template='schedule/form.html', extra_context=context_vars)
