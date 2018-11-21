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
class UserMessage(models.Model):
    """
    Model with user emails

    target_email - target email to send message
    text - content of the message
    status - status either send or not
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_messages', default=0)
    # message template name
    user_message_name = models.CharField(max_length=100)
    # message template description
    user_message_description = models.CharField(max_length=500)
    # message tags
    user_message_tags = TaggableManager(blank=True)    
    # message target email
    user_message_target_email = models.EmailField(max_length=100)
    # message email title
    user_message_email_title = models.CharField(max_length=50, default='Mail from mailsender')
    # message text
    user_message_text = models.CharField(max_length=500)
    # message send status
    user_message_sent_status = models.BooleanField(default=False)
    # message send datatime
    user_message_sent_datetime = models.DateTimeField(default=now)

    class Meta:
        verbose_name_plural = 'Users Messages'

    def get_short_description(self):
        """
        Get short(<50) message description text
        """
        return self.user_message_description if len(self.user_message_description) < 50 else self.user_message_description[:50] + ' ...'

    def get_all_tags(self):
        """
        Get list of message tag's
        """
        return [tag.name for tag in self.user_message_tags.all()]

    def __str__(self):
            return f'Author: {self.user.username}; Name: {self.user_message_name}'
            