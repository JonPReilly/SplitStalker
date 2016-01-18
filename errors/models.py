from __future__ import unicode_literals

from django.db import models

from django.utils.encoding import smart_unicode

class MiscError(models.Model):
	error_type = models.CharField(max_length = 120)
	error_data = models.CharField(max_length = 120)
	error_explination = models.TextField(max_length = 3000)
	
	error_time = models.DateTimeField(auto_now = True)

	def __unicode__(self):
		return smart_unicode(self.error_type)

class FailedEmail(models.Model):
	email = models.EmailField(null=False, blank = False)
	subject = models.CharField(max_length = 120)
	body = models.TextField(max_length = 3000)

	error_time = models.DateTimeField(auto_now = True)
	def __unicode__(self):
		return smart_unicode(self.email)
