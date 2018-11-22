from django.db import models
from django.contrib.auth.models import Group, User
from django.utils.timezone import now

from taggit.managers import TaggableManager


# user
class MailerUser(models.Model):
    """
    Model improve standard User model.
    
    mailer_user - one-to-one with User
    mailer_company - company name
    mailer_company_address - company address
    mailer_phone_number - contact phone
    mailer_company_industry - company industry
    mailer_company_website - company website
    mailer_user_status - user status (3 variants)
    """
    # user
    mailer_user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_account')
    # company name
    mailer_company = models.CharField(max_length=250)
    # company address
    mailer_company_address = models.CharField(max_length=250)
    # contact number
    mailer_phone_number = models.CharField(max_length=30)
    # industry
    mailer_company_industry = models.CharField(max_length=250)
    # website
    mailer_company_website = models.CharField(max_length=250)
    # user status
    not_confirmed_user = "NCN"
    mail_confirmed_user = "MCN"
    admin_confirmed_user = "ACN"
    user_status_choice = (
        (not_confirmed_user, 'Not confirmed mail'),
        (mail_confirmed_user, 'Confirmed mails'),
        (admin_confirmed_user, 'Admin confirmed'),
    )
    mailer_user_status = models.CharField(max_length=3,
                                          choices=user_status_choice,
                                          default=not_confirmed_user,
                                          verbose_name='user status')
    # users account type
    free_account_type = "FREE"
    premium_account_type = "PREM"
    user_account_type = (
        (free_account_type, 'Free account'),
        (premium_account_type, 'Premium account'),
    )

    mailer_account_type = models.CharField(choices=user_account_type,
                                           default=free_account_type,
                                           verbose_name='account type',
                                           max_length=4)

    class Meta:
        verbose_name_plural = 'Users List'

    def __str__(self):
        return f'User: {self.mailer_user.username}; User status: {self.get_mailer_user_status_display()};'


# user emails
class UserEmails(models.Model):
    """
    Model with user emails

    mailer_first_email - user's first email
    mailer_first_email_status - first email status of verification (True - verified, False - not)
    mailer_second_email - user's second email
    mailer_second_email_status - second email status of verification (True - verified, False - not)
    mailer_with_single_email - if user check only one email
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_emails', default=0, primary_key=True)

    mailer_first_email = models.EmailField(max_length=100, unique=True)
    mailer_first_email_status = models.BooleanField(default=False)

    mailer_second_email = models.EmailField(max_length=100, unique=False, blank=True, null=True)
    mailer_second_email_status = models.BooleanField(default=False)

    mailer_with_single_email = models.BooleanField(default=False)
    
    class Meta:
        verbose_name_plural = 'Users Emails List'
    
    def __str__(self):
        return f'User: {self.user.username}; Mail: {self.mailer_first_email}'


class DomainBlackList(models.Model):
    """
    Model with black list domains

    name - domain that don't satisfy requirements
    """
    name = models.CharField(max_length=60)

    class Meta:
        verbose_name_plural = 'Domains Black List'

    def __str__(self):
        return self.name


# user sent emails
class Campaign(models.Model):
    """
    Model with user emails

    target_email - target email to send message
    text - content of the message
    status - status either send or not
    """
    #user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_campaign', default=0)
    # message template name
    campaign_name = models.CharField(max_length=100)
    # message template description
    campaign_description = models.CharField(max_length=500)
    # message tags
    campaign_tags = TaggableManager(blank=True)    
    # message target email
    #campaign_target_email = models.EmailField(max_length=100)
    # message email title
    #campaign_email_title = models.CharField(max_length=50, default='Mail from mailsender')
    # message text
    campaign_text = models.CharField(max_length=500)
    # message send status
    #campaign_sent_status = models.BooleanField(default=False)
    # message send datatime
    #campaign_sent_datetime = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Users Campaigns'

    def get_short_description(self):
        """
        Get short(<50) message description text
        """
        return self.campaign_description if len(self.campaign_description) < 50 else self.campaign_description[:50] + ' ...'

    def get_all_tags(self):
        """
        Get list of message tag's
        """
        return [tag.name for tag in self.campaign_tags.all()]

    def delete_all_tags(self):
        """
        Delete all tags from input field
        :return:
        """
        return self.campaign_tags.clear()

    def __str__(self):
            return f'Campaign: {self.campaign_name}'


class AttachedFiles(models.Model):
    file = models.FileField(upload_to='attached_files', null=True, blank=True)
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='campaign_files',
                                 null=True, blank=True)


class UserSavedMessages(models.Model):
    """
    Model with user saved campaigns

    text - content of the message
    status - status either send or not
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_saved_messages', default=0)
    saved_campaign = models.OneToOneField(Campaign, on_delete=models.CASCADE, related_name='saved_campaign',
                                          primary_key=True)

    campaign_sent_status = models.BooleanField(default=False)
    # message send datetime
    campaign_sent_datetime = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Users Saved Campaigns'

    def __str__(self):
            return f'User: {self.user}'
