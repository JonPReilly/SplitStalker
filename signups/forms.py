from django.forms import *
from django import forms

from .models import Athlete

class AddAthleteForm(ModelForm):
	
	
	class Meta:
		model = Athlete
		fields = ['name' , 'school']