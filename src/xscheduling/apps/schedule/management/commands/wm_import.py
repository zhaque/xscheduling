from datetime import datetime, timedelta
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import CommandError
from django.core.management.base import NoArgsCommand
from client.models import Client
from job.models import Job
from staff.models import Staff
from supplier.models import Supplier, Contact
from workflowmax.client.models import Client as WorkflowmaxClient
from workflowmax.job.models import Job as WorkflowmaxJob
from workflowmax.staff.models import Staff as WorkflowmaxStaff
from workflowmax.supplier.models import Supplier as WorkflowmaxSupplier

class Command(NoArgsCommand):
  help = 'Import Workflowmax data.'
  def handle_noargs(self, **options):
      self.wm_import()

  def wm_import_clients(self):
    for client in Client.objects.all():
      client.delete()
    wm_clients = WorkflowmaxClient.objects.all()
    for wm_client in wm_clients:
      client = Client()
      client.wm_import(wm_client)

  def wm_import_stuff(self):
    for staff in Staff.objects.all():
      staff.delete()
    wm_staff_list = WorkflowmaxStaff.objects.all()
    for wm_staff in wm_staff_list:
      staff = Staff()
      staff.wm_import(wm_staff)

  def wm_import_suppliers(self):
    for supplier in Supplier.objects.all():
      supplier.delete()
    wm_suppliers = WorkflowmaxSupplier.objects.all()
    for wm_supplier in wm_suppliers:
      supplier = Supplier()
      supplier.wm_import(wm_supplier)

  def wm_import_job(self):
    for job in Job.objects.all():
      job.delete()
    wm_jobs = WorkflowmaxJob.objects.all(datetime.now() - timedelta(days=365), datetime.now() + timedelta(days=365))
    for wm_job in wm_jobs:
      job = Job()
      job.wm_import(wm_job)

  def wm_import(self):
    self.wm_import_clients()
    self.wm_import_stuff()
    self.wm_import_suppliers()
    self.wm_import_job()






