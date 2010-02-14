from django.views.generic.simple import direct_to_template
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
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
    try:
      api = Api.objects.get(id=object_id, user=request.user)
      if not api.enabled:
        api.enabled = True
        api.save()
    except ObjectDoesNotExist:
      pass
    api = Api.objects.filter(id=object_id, user=request.user)
    json = serializers.serialize('json', api)
    return HttpResponse(json, mimetype="application/json")

@login_required
def disable_api(request, object_id):
  if request.method == "POST":
    try:
      api = Api.objects.get(id=object_id, user=request.user)
      if api.enabled:
        api.enabled = False
        api.save()
    except ObjectDoesNotExist:
      pass
    api = Api.objects.filter(id=object_id, user=request.user)
    json = serializers.serialize('json', api)
    return HttpResponse(json, mimetype="application/json")

@login_required
def set_apikey(request, object_id):
  if request.method == "POST":
    new_key = request.POST.get('apikey','')
    try:
      api = Api.objects.get(id=object_id, user=request.user)
      api.api_key = new_key
      api.save()
    except ObjectDoesNotExist:
      pass
    api = Api.objects.filter(id=object_id, user=request.user)
    json = serializers.serialize('json', api)
    return HttpResponse(json, mimetype="application/json")
