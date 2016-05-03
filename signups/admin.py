from django.contrib import admin
from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


from .models import Athlete
from .models import LastMeet
from .models import Stalker



class StalkerInline(admin.StackedInline):
    model = Stalker
    can_delete = False
    raw_id_fields  = ['following_athletes']
    verbose_name_plural = 'stalker'

class UserAdmin(BaseUserAdmin):
    inlines = (StalkerInline, )



class LastMeetAdmin(admin.ModelAdmin):
	search_fields = ['name','last_url']
	class Meta:
		model = LastMeet

class AthleteAdmin(admin.ModelAdmin):
	search_fields = ['name', 'school']

	list_filter = (
        ('created_by', admin.RelatedOnlyFieldListFilter),
    )

	class Meta:
		model = Athlete



class StalkerAdmin(admin.ModelAdmin):
	raw_id_fields  = ['following_athletes']
	class Meta:
		model = Stalker


admin.site.unregister(User)
admin.site.register(Stalker, StalkerAdmin)
admin.site.register(User, UserAdmin)

admin.site.register(Athlete,AthleteAdmin)
admin.site.register(LastMeet,LastMeetAdmin)
