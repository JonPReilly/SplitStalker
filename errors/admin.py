from django.contrib import admin

from .models import FailedEmail
from .models import MiscError

# Register your models here.


class FailedEmailAdmin(admin.ModelAdmin):
	readonly_fields = ('error_time',)
	class Meta:
		model = FailedEmail

class MiscErrorAdmin(admin.ModelAdmin):
	readonly_fields = ('error_time',)
	class Meta:
		model = MiscError

admin.site.register(FailedEmail, FailedEmailAdmin)
admin.site.register(MiscError, MiscErrorAdmin)