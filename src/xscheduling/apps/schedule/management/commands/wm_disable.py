from datetime import datetime, timedelta
from django.conf import settings
from django.core import management
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import CommandError
from django.core.management.base import NoArgsCommand
from job.models import JobState

class Command(NoArgsCommand):
  help = 'Disable Workflowmax sync.'
  def handle_noargs(self, **options):
      self.wm_disable()

  def wm_disable(self):
    JobState.objects.all().delete()
    # What should we do with current jobs?
#    management.call_command('flush', verbosity=0, interactive=False)
    management.call_command('loaddata', 'state_data.yaml', verbosity=1)