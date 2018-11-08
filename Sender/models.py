from django.db import models
from django.contrib.auth.models import Group, User
from django.utils.timezone import now


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
    mailer_user = models.OneToOneField(User, on_delete = models.CASCADE, related_name='user_account')
    # company name
    mailer_company = models.CharField(max_length = 250)
    # company address
    mailer_company_address = models.CharField(max_length = 250)
    # contact number
    mailer_phone_number = models.CharField(max_length = 30)
    # industry
    mailer_company_industry = models.CharField(max_length = 250)
    # website
    mailer_company_website = models.CharField(max_length = 250)
    # user status
    not_confirmed_user = "NCN"
    mail_confirmed_user = "MCN"
    admin_confirmed_user = "ACN"
    user_status_choice = (
        (not_confirmed_user, 'Not confirmed mail'),
        (mail_confirmed_user, 'Confirmed mail'),
        (admin_confirmed_user, 'Admin confirmed'),
    )
    mailer_user_status = models.CharField(max_length = 3,
                                          choices = user_status_choice,
                                          default = not_confirmed_user,
                                          verbose_name = 'user status')

    def __str__(self):
        return f'User: {self.mailer_user.username}; User status: {self.get_mailer_user_status_display()};'

