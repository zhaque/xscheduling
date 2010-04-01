from django.utils.text import capfirst
from django.utils.translation import ugettext as _
from django.views.generic.simple import direct_to_template

def root(request):
  context_vars = dict()
  context_vars['header'] = capfirst(_('workflowmax'))
  return direct_to_template(request, template='workflowmax/root.html', extra_context=context_vars)

