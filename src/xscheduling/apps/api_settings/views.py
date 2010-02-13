from django.views.generic.simple import direct_to_template

def list_api(request):
  context_vars = dict()
  return direct_to_template(request, template='api_settings/list_api.html', extra_context=context_vars)
