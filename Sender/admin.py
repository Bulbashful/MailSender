from django.contrib import admin
from .models import MailerUser, UserEmails

admin.site.register(MailerUser)
admin.site.register(UserEmails)
