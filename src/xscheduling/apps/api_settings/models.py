from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

class Api(models.Model):
  name = models.CharField(_('name'), max_length=255)
  uri = models.URLField(_('URI'))
  api_key = models.CharField(_('API key'), max_length=150, null=True, blank=True)
  user = models.ForeignKey(User, verbose_name=_('user'))
  enabled = models.BooleanField(_('enabled'), default=True)
  optional = models.BooleanField(_('optional'), default=False)
  
  class Meta:
    ordering = ['name']
    unique_together = ('user', 'api_key')
    verbose_name = _('API')
    verbose_name_plural = _('APIs')

  def __unicode__(self):
    return _('%s for %s') % (self.name, self.user)

  def save(self):
    if not self.optional and not self.api_key:
      raise ValueError("You must provide default API key.")
    super(Api, self).save()

  def clean(self):
    if not self.optional and not self.api_key:
      raise ValidationError(_('You must provide default API key.'))
