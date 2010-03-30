from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.utils.text import capfirst
from django.utils.translation import ugettext as _
from django.views.generic.simple import direct_to_template
from datetime import datetime, timedelta
import simplejson

class CalendarEvent(object):
  id = ''
  title = ''
  allDay = ''
  start = None
  end = None
  url = ''

@login_required
def calendar(request):
  context_vars = dict()
  context_vars['user'] = request.user
  context_vars['header'] = capfirst(_('calendar'))
  return direct_to_template(request, template='fullcalendar/cal.html', extra_context=context_vars)

@login_required
def events(request):
  start = request.GET.get('start', None)
  end = request.GET.get('end', None)
  try:
    start = datetime.fromtimestamp(float(start))
    end = datetime.fromtimestamp(float(end))
  except ValueError:
    raise

  events = (
    dict(id=111, title='Event1', allDay=True, start=datetime.now().ctime()),
    dict(id=222, title='Event2', allDay=False, start=datetime.now().ctime(), end=(datetime.now()+timedelta(hours=1)).ctime()),
  )
#  try:
#    api = Api.objects.get(id=object_id, user=request.user)
#    if not api.enabled:
#      api.enabled = True
#      api.save()
#  except ObjectDoesNotExist:
#    pass
#  api = Api.objects.filter(id=object_id, user=request.user)
#  json = serializers.serialize('json', events)
  json = simplejson.dumps(events)
  return HttpResponse(json, mimetype="application/json")
