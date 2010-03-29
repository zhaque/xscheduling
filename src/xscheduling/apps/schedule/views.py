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

def root(request):
  return direct_to_template(request, template='schedule/root.html')

@login_required
def calendar(request):
#  token = request.GET.get('token', '')
#  if not token:
#    url = 'https://www.google.com/accounts/AuthSubRequest?next=http%3A%2F%2F127.0.0.1:8000%2Fschedule%2F&scope=http%3A%2F%2Fwww.google.com%2Fcalendar%2Ffeeds%2F&session=1&secure=0&hd=cooperativegardeners.com'
#    return HttpResponseRedirect(url)
#
#  calendar_service = gdata.calendar.service.CalendarService(server='cooperativegardeners.com', token_store=(token,))
#  calendar_service.UpgradeToSessionToken()

  context_vars = dict()
  context_vars['user'] = request.user
  return direct_to_template(request, template='schedule/cal.html', extra_context=context_vars)

# Client views
@login_required
def list_clients(request):
  context_vars = dict()
  context_vars['header'] = capfirst(_('client list'))
  context_vars['clients'] = Client.objects.all()
  return direct_to_template(request, template='schedule/list.html', extra_context=context_vars)

@login_required
def get_client(request, object_id):
  try:
    object_id = int(object_id)
  except ValueError:
    return HttpResponseRedirect(reverse('schedule-client-list'))
  context_vars = dict()
  context_vars['header'] = '%s %d' % (capfirst(_('client')), object_id)
  context_vars['client'] = Client.objects.get(id=object_id)
  return direct_to_template(request, template='schedule/view.html', extra_context=context_vars)

@login_required
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
  
  context_vars['form'] = form
  context_vars['helper'] = helper
  return direct_to_template(request, template='schedule/form.html', extra_context=context_vars)

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
      return HttpResponseRedirect(reverse('schedule-client', args=[client.id]))
  
  context_vars['form'] = form
  context_vars['helper'] = helper
  return direct_to_template(request, template='schedule/form.html', extra_context=context_vars)

@login_required
def delete_client(request, object_id):
  try:
    object_id = int(object_id)
  except ValueError:
    return HttpResponseRedirect(reverse('schedule-client-list'))
  context_vars = dict()
  context_vars['header'] = '%s %d' % (capfirst(_('delete client')), object_id)
  context_vars['comment'] = _('You are trying to delete client "%d". Sure?') % object_id
  client = Client.objects.get(id=object_id)
  
  if request.method == "POST":
    client.delete()
    return HttpResponseRedirect(reverse('schedule-client-list'))

  return direct_to_template(request, template='schedule/delete.html', extra_context=context_vars)

@login_required
def add_client_contact(request, object_id):
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
      return HttpResponseRedirect(reverse('schedule-client', args=[object_id]))
  
  context_vars['form'] = form
  context_vars['helper'] = helper
  return direct_to_template(request, template='schedule/form.html', extra_context=context_vars)

@login_required
def edit_client_contact(request, owner_id, object_id):
  try:
    owner_id = int(owner_id)
  except ValueError:
    return HttpResponseRedirect(reverse('schedule-client-list'))
  try:
    object_id = int(object_id)
  except ValueError:
    return HttpResponseRedirect(reverse('schedule-client', args=[owner_id]))
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
      return HttpResponseRedirect(reverse('schedule-client', args=[owner_id]))
  
  context_vars['form'] = form
  context_vars['helper'] = helper
  return direct_to_template(request, template='schedule/form.html', extra_context=context_vars)

# Staff views

@login_required
def list_staff(request):
  context_vars = dict()
  context_vars['header'] = capfirst(_('staff list'))
  context_vars['staff_list'] = Staff.objects.all()
  return direct_to_template(request, template='schedule/list.html', extra_context=context_vars)

@login_required
def get_staff(request, object_id):
  try:
    object_id = int(object_id)
  except ValueError:
    return HttpResponseRedirect(reverse('schedule-staff-list'))
  context_vars = dict()
  context_vars['header'] = '%s %d' % (capfirst(_('staff')), object_id)
  context_vars['staff'] = Staff.objects.get(id=object_id)
  return direct_to_template(request, template='schedule/view.html', extra_context=context_vars)

@login_required
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
  
  context_vars['form'] = form
  context_vars['helper'] = helper
  return direct_to_template(request, template='schedule/form.html', extra_context=context_vars)

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
      return HttpResponseRedirect(reverse('schedule-staff', args=[staff.id]))
  
  context_vars['form'] = form
  context_vars['helper'] = helper
  return direct_to_template(request, template='schedule/form.html', extra_context=context_vars)

@login_required
def delete_staff(request, object_id):
  try:
    object_id = int(object_id)
  except ValueError:
    return HttpResponseRedirect(reverse('schedule-staff-list'))
  context_vars = dict()
  context_vars['header'] = '%s %d' % (capfirst(_('delete staff')), object_id)
  context_vars['comment'] = _('You are trying to delete staff "%d". Sure?') % object_id
  staff = Staff.objects.get(id=object_id)
  
  if request.method == "POST":
    staff.delete()
    return HttpResponseRedirect(reverse('schedule-staff-list'))

  return direct_to_template(request, template='schedule/delete.html', extra_context=context_vars)

@login_required
def get_staff_jobs(request, object_id):
  try:
    object_id = int(object_id)
  except ValueError:
    return HttpResponseRedirect(reverse('schedule-staff-list'))
  context_vars = dict()
  context_vars['header'] = '%s %d' % (capfirst(_('job list for staff')), object_id)
  staff = Staff.objects.get(id=object_id)
  context_vars['staff'] = staff
  context_vars['jobs'] = Job.objects.filter(staff=staff)
  return direct_to_template(request, template='schedule/list.html', extra_context=context_vars)


# Supplier views
@login_required
def list_suppliers(request):
  context_vars = dict()
  context_vars['header'] = capfirst(_('suppliers list'))
  context_vars['suppliers'] = Supplier.objects.all()
  return direct_to_template(request, template='schedule/list.html', extra_context=context_vars)

@login_required
def get_supplier(request, object_id):
  try:
    object_id = int(object_id)
  except ValueError:
    return HttpResponseRedirect(reverse('schedule-supplier-list'))
  context_vars = dict()
  context_vars['header'] = '%s %d' % (capfirst(_('supplier')), object_id)
  context_vars['supplier'] = Supplier.objects.get(id=object_id)
  return direct_to_template(request, template='schedule/view.html', extra_context=context_vars)

@login_required
def edit_supplier(request, object_id):
  try:
    object_id = int(object_id)
  except ValueError:
    return HttpResponseRedirect(reverse('schedule-supplier-list'))
  context_vars = dict()
  context_vars['header'] = '%s %d' % (capfirst(_('supplier')), object_id)
  supplier = Supplier.objects.get(id=object_id)
  form = SupplierForm(supplier.to_dict())
  helper = FormHelper()
  helper.form_class = 'uniform'
  submit = Submit('save',_('save'))
  helper.add_input(submit)
  if request.method == "POST":
    form = SupplierForm(request.POST, request.FILES)
    if form.is_valid():
      supplier.name = form.cleaned_data['name']
      supplier.address = form.cleaned_data['address']
      supplier.postal_address = form.cleaned_data['postal_address']
      supplier.phone = form.cleaned_data['phone']
      supplier.fax = form.cleaned_data['fax']
      supplier.website = form.cleaned_data['website']
      supplier.referral_source = form.cleaned_data['referral_source']
      supplier.save()
      return HttpResponseRedirect(reverse('schedule-supplier', args=[supplier.id]))
  
  context_vars['form'] = form
  context_vars['helper'] = helper
  return direct_to_template(request, template='schedule/form.html', extra_context=context_vars)

@login_required
def add_supplier(request):
  context_vars = dict()
  context_vars['header'] = capfirst(_('add new supplier'))
  form = SupplierForm()
  helper = FormHelper()
  helper.form_class = 'uniform'
  submit = Submit('save',_('save'))
  helper.add_input(submit)
  if request.method == "POST":
    form = SupplierForm(request.POST, request.FILES)
    if form.is_valid():
      supplier = Supplier()
      supplier.name = form.cleaned_data['name']
      supplier.address = form.cleaned_data['address']
      supplier.postal_address = form.cleaned_data['postal_address']
      supplier.phone = form.cleaned_data['phone']
      supplier.fax = form.cleaned_data['fax']
      supplier.website = form.cleaned_data['website']
      supplier.referral_source = form.cleaned_data['referral_source']
      supplier = supplier.save()
      return HttpResponseRedirect(reverse('schedule-supplier', args=[supplier.id]))
  
  context_vars['form'] = form
  context_vars['helper'] = helper
  return direct_to_template(request, template='schedule/form.html', extra_context=context_vars)

@login_required
def delete_supplier(request, object_id):
  try:
    object_id = int(object_id)
  except ValueError:
    return HttpResponseRedirect(reverse('schedule-supplier-list'))
  context_vars = dict()
  context_vars['header'] = '%s %d' % (capfirst(_('delete supplier')), object_id)
  context_vars['comment'] = _('You are trying to delete supplier "%d". Sure?') % object_id
  supplier = Supplier.objects.get(id=object_id)
  
  if request.method == "POST":
    supplier.delete()
    return HttpResponseRedirect(reverse('schedule-supplier-list'))

  return direct_to_template(request, template='schedule/delete.html', extra_context=context_vars)

@login_required
def add_supplier_contact(request, object_id):
  try:
    object_id = int(object_id)
  except ValueError:
    return HttpResponseRedirect(reverse('schedule-supplier-list'))
  context_vars = dict()
  context_vars['header'] = capfirst(_('add new contact for supplier %d') % object_id)
  form = ContactForm()
  helper = FormHelper()
  helper.form_class = 'uniform'
  submit = Submit('save',_('save'))
  helper.add_input(submit)
  if request.method == "POST":
    form = ContactForm(request.POST, request.FILES)
    if form.is_valid():
      contact = SupplierContact()
      contact.owner_id = object_id
      contact.name = form.cleaned_data['name']
      contact.mobile = form.cleaned_data['mobile']
      contact.email = form.cleaned_data['email']
      contact.phone = form.cleaned_data['phone']
      contact.position = form.cleaned_data['position']
      contact = contact.save()
      return HttpResponseRedirect(reverse('schedule-supplier', args=[object_id]))
  
  context_vars['form'] = form
  context_vars['helper'] = helper
  return direct_to_template(request, template='schedule/form.html', extra_context=context_vars)

@login_required
def edit_supplier_contact(request, owner_id, object_id):
  try:
    owner_id = int(owner_id)
  except ValueError:
    return HttpResponseRedirect(reverse('schedule-supplier-list'))
  try:
    object_id = int(object_id)
  except ValueError:
    return HttpResponseRedirect(reverse('schedule-supplier', args=[owner_id]))
  context_vars = dict()
  context_vars['header'] = capfirst(_('edit contact %d') % object_id)
  contact = SupplierContact.objects.get(id=object_id)
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
      return HttpResponseRedirect(reverse('schedule-supplier', args=[owner_id]))
  
  context_vars['form'] = form
  context_vars['helper'] = helper
  return direct_to_template(request, template='schedule/form.html', extra_context=context_vars)

#Job views
@login_required
def list_jobs(request):
  context_vars = dict()
  context_vars['header'] = capfirst(_('current job list'))
  context_vars['jobs'] = Job.objects.current()
  return direct_to_template(request, template='schedule/list.html', extra_context=context_vars)

@login_required
def get_job(request, object_id):
  context_vars = dict()
  context_vars['header'] = '%s %s' % (capfirst(_('job')), object_id)
  context_vars['job'] = Job.objects.get(id=object_id)
  return direct_to_template(request, template='schedule/view.html', extra_context=context_vars)
  
@login_required
def add_job(request):
  context_vars = dict()
  context_vars['header'] = capfirst(_('add new job'))
  form = AddJobForm()
  helper = FormHelper()
  helper.form_class = 'uniform'
  submit = Submit('save',_('save'))
  helper.add_input(submit)
  if request.method == "POST":
    form = AddJobForm(request.POST, request.FILES)
    if form.is_valid():
      job = Job()
      job.name = form.cleaned_data['name']
      job.description = form.cleaned_data['description']
      job.start_date = strptime(form.cleaned_data['start_date'], '%Y%m%d')
      job.due_date = strptime(form.cleaned_data['due_date'], '%Y%m%d')
      client_id = form.cleaned_data['client']
      client = Client.objects.get(id=client_id)
      job.clients = [client,]
      job = job.save()
      return HttpResponseRedirect(reverse('schedule-job', args=[job.id]))
  
  context_vars['form'] = form
  context_vars['helper'] = helper
  return direct_to_template(request, template='schedule/form.html', extra_context=context_vars)

@login_required
def edit_job(request, object_id):
  context_vars = dict()
  context_vars['header'] = '%s %s' % (capfirst(_('job')), object_id)
  job = Job.objects.get(id=object_id)
  form = EditJobForm(job.to_dict())
  helper = FormHelper()
  helper.form_class = 'uniform'
  submit = Submit('save',_('save'))
  helper.add_input(submit)
  if request.method == "POST":
    form = EditJobForm(request.POST, request.FILES)
    if form.is_valid():
      job.state = form.cleaned_data['state']
      if form.cleaned_data['assigned']:
        job.assigned = []
        for assigned_id in form.cleaned_data['assigned']:
          try:
            job.assigned.append(Staff.objects.get(id=assigned_id))
          except ResponseStatusError:
            pass
      job.save()
      return HttpResponseRedirect(reverse('schedule-job', args=[job.id]))
  
  context_vars['form'] = form
  context_vars['helper'] = helper
  return direct_to_template(request, template='schedule/form.html', extra_context=context_vars)

@login_required
def delete_job(request, object_id):
  context_vars = dict()
  context_vars['header'] = '%s %s' % (capfirst(_('delete job')), object_id)
  context_vars['comment'] = _('You are trying to delete job "%s". Sure?') % object_id
  job = Job.objects.get(id=object_id)
  
  if request.method == "POST":
    job.delete()
    return HttpResponseRedirect(reverse('schedule-job-list'))

  return direct_to_template(request, template='schedule/delete.html', extra_context=context_vars)

@login_required
def add_job_note(request, object_id):
  job = Job.objects.get(id=object_id)
  context_vars = dict()
  context_vars['header'] = capfirst(_('add new note for job %s') % job.id)
  form = NoteForm()
  helper = FormHelper()
  helper.form_class = 'uniform'
  submit = Submit('save',_('save'))
  helper.add_input(submit)
  if request.method == "POST":
    form = NoteForm(request.POST, request.FILES)
    if form.is_valid():
      note = Note()
      note.owner_id = job.id
      note.title = form.cleaned_data['title']
      note.text = form.cleaned_data['text']
      note.folder = form.cleaned_data['folder']
      note.public = form.cleaned_data['public']
      note.save()
      return HttpResponseRedirect(reverse('schedule-job', args=[job.id]))
  context_vars['form'] = form
  context_vars['helper'] = helper
  
  return direct_to_template(request, template='schedule/form.html', extra_context=context_vars)

@login_required
def edit_job_task(request, owner_id, object_id):
  try:
    object_id = int(object_id)
  except ValueError:
    return HttpResponseRedirect(reverse('schedule-job', args=[owner_id]))
  context_vars = dict()
  context_vars['header'] = capfirst(_('edit task %d') % object_id)
#  task = Task.objects.get(id=object_id)
  job = Job.objects.get(id=owner_id)
  for task_obj in job.tasks:
    if task_obj.id == object_id:
      task = task_obj
  if not task:
    return HttpResponseRedirect(reverse('schedule-job', args=[owner_id]))

  task = Task(xml_object=task)
  form = TaskForm(task.to_dict())
  helper = FormHelper()
  submit = Submit('save',_('save'))
  helper.add_input(submit)
  if request.method == "POST":
    form = TaskForm(request.POST, request.FILES)
    if form.is_valid():
      task.owner_id = job.id
      task.name = form.cleaned_data['name']
      task.description = form.cleaned_data['description']
      task.estimated_minutes = form.cleaned_data['estimated_minutes']
#      task.actual_minutes = form.cleaned_data['actual_minutes']
#      task.completed = form.cleaned_data['completed']
#      task.billable = form.cleaned_data['billable']
#      task.start_date = form.cleaned_data['start_date']
#      task.due_date = form.cleaned_data['due_date']
#      task.completed = form.cleaned_data['completed']
#      if form.cleaned_data['assigned']:
#        task.assigned = []
#        for assigned_id in form.cleaned_data['assigned']:
#          try:
#            task.assigned.append(Staff.objects.get(id=assigned_id))
#          except ResponseStatusError:
#            pass
      task.save()
      return HttpResponseRedirect(reverse('schedule-job', args=[owner_id]))
  
  context_vars['form'] = form
  context_vars['helper'] = helper
  return direct_to_template(request, template='schedule/form.html', extra_context=context_vars)



