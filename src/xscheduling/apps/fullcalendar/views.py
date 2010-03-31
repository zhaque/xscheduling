from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.utils.text import capfirst
from django.utils.translation import ugettext as _
from django.views.generic.simple import direct_to_template
from datetime import datetime, timedelta
import simplejson
from google_cal import client_login, get_events
from staff.models import Staff

@login_required
def calendar(request):
  context_vars = dict()
  context_vars['user'] = request.user
  context_vars['header'] = capfirst(_('calendar'))
  return direct_to_template(request, template='fullcalendar/cal.html', extra_context=context_vars)

@login_required
def events(request):
  try:
    staff = Staff.objects.get(user_ptr=request.user)
  except ObjectDoesNotExist:
    pass

  start = request.GET.get('start', None)
  end = request.GET.get('end', None)
  try:
    start = datetime.fromtimestamp(float(start))
    end = datetime.fromtimestamp(float(end))
  except ValueError:
    raise
  
  admin_email = '%s@%s' % (settings.GAPPS_USERNAME, settings.GAPPS_DOMAIN)
  srv = client_login(admin_email, settings.GAPPS_PASSWORD)
  events = get_events(srv, start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'))
  
  json = simplejson.dumps(events)
  return HttpResponse(json, mimetype="application/json")
