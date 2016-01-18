from __future__ import unicode_literals
 
from django.utils.encoding import smart_unicode
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import m2m_changed
from django.core.exceptions import ValidationError


class Error(models.Model):
	error_type = models.CharField(max_length = 120)
	error_data = models.CharField(max_length = 120)
	error_explination = models.TextField(max_length = 3000)
	def __unicode__(self):
		return smart_unicode(error_type)

class Athlete(models.Model):
	school = models.CharField(max_length = 120)
	name = models.CharField(max_length = 120)
	url = models.CharField(max_length = 120)
	def __unicode__(self):
		return smart_unicode(self.name) + " (" + smart_unicode(self.school) +")"

class Stalker(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, unique = True)
	following_athletes = models.ManyToManyField(Athlete, blank = True, verbose_name = 'Athletes User is Following')
	
	def __unicode__(self):
		return smart_unicode(self.user)
	

class LastMeet(models.Model):
	name = models.CharField(max_length = 120, default = "Meet")
	last_url = models.CharField(max_length = 120, unique = True)
	meets_processed = models.IntegerField(default = 0)
	def __unicode__(self):
		return smart_unicode(self.name + " (" + self.last_url + ")")
