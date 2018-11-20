from django.contrib import admin
from .models import MailerUser, UserEmails, DomainBlackList, UserMessage


class MailerUserAdmin(admin.ModelAdmin):
    # поля для фильтрации
    list_filter = ('mailer_user_status',)


admin.site.register(MailerUser, MailerUserAdmin)
admin.site.register(UserEmails)
admin.site.register(DomainBlackList)
admin.site.register(UserMessage)
