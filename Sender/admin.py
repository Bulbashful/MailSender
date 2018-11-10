from django.contrib import admin
from .models import MailerUser, UserEmails, DomainBlackList

admin.site.register(MailerUser)
admin.site.register(UserEmails)
admin.site.register(DomainBlackList)
