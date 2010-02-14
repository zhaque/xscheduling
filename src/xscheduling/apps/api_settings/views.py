from django.views.generic.simple import direct_to_template
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.http import HttpResponse
from django.utils.text import capfirst
from django.utils.translation import ugettext as _
from api_settings.models import Api

@login_required
def list_api(request):
  context_vars = dict()
  context_vars['header'] = capfirst(_('user API list'))
  context_vars['apis'] = Api.objects.filter(user=request.user)
  return direct_to_template(request, template='api_settings/list.html', extra_context=context_vars)

@login_required
def enable_api(request, object_id):
  if request.method == "POST":
    api = Api.objects.get(id=object_id)
    if not api.enabled:
      api.enabled = True
      api.save()
    api = Api.objects.filter(id=object_id)
    json = serializers.serialize('json', api)
    return HttpResponse(json, mimetype="application/json")

@login_required
def disable_api(request, object_id):
  if request.method == "POST":
    api = Api.objects.get(id=object_id)
    if api.enabled:
      api.enabled = False
      api.save()
    api = Api.objects.filter(id=object_id)
    json = serializers.serialize('json', api)
    return HttpResponse(json, mimetype="application/json")
  