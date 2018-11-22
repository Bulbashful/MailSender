from django.contrib import admin
from .models import MailerUser, UserEmails, DomainBlackList, Campaign, AttachedFiles, UserSavedMessages


class FilesInline(admin.StackedInline):
    model = AttachedFiles
    extra = 1


class CampaignAdminPage(admin.ModelAdmin):
    inlines = [FilesInline]

    def save_model(self, request, obj, form, change):
        obj.save()
        for afile in request.FILES.getlist('photos_multiple'):
            obj.photos.create(image=afile)


class MailerUserAdmin(admin.ModelAdmin):
    # поля для фильтрации
    list_filter = ('mailer_user_status',)


admin.site.register(MailerUser, MailerUserAdmin)
admin.site.register(UserEmails)
admin.site.register(DomainBlackList)
admin.site.register(Campaign, CampaignAdminPage)
admin.site.register(AttachedFiles)
admin.site.register(UserSavedMessages)
