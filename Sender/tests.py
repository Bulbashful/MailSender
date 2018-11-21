from django.test import TestCase, Client
from .models import MailerUser, User, UserEmails
from . import forms


class MailerUserTestCase(TestCase):
    def setUp(self):
        user = User.objects.create(username='John Smith')
        MailerUser.objects.create(mailer_user=user,
                                  mailer_company='Apple',
                                  mailer_company_address='Gomel',
                                  mailer_phone_number='+375294332312',
                                  mailer_company_industry='HZ',
                                  mailer_company_website='aaasolutions.by',
                                  )
        UserEmails.objects.create(user=user,
                                  mailer_first_email='test@gmail.com',
                                  mailer_second_email='test@yandex.by')

    def test_get_user(self):
        user = User.objects.get(username='John Smith')
        mailer_user = MailerUser.objects.get(mailer_user=user)
        self.assertEqual(mailer_user.mailer_company_address, 'Gomel')
        self.assertEqual(mailer_user.mailer_user_status, 'NCN')

    def test_check_user_emails(self):
        user = User.objects.get(username='John Smith')
        user_emails = UserEmails.objects.get(user=user)
        self.assertEqual(user_emails.mailer_first_email_status, False)
        self.assertEqual(user_emails.mailer_second_email_status, False)


class LoginTestCase(MailerUserTestCase, TestCase):

    def test_login_post(self):
        user = User.objects.get(username='John Smith')
        # mailer_user = MailerUser.objects.get(mailer_user=user)
        login_credentials = {'username': user.username, 'password': user.password}
        response = self.client.post('/login/', data=login_credentials)
        self.assertEqual(response.status_code, 302)

    def test_login(self):
        user = User.objects.get(username='John Smith')
        user.set_password('12345')
        user.save()
        client = Client()
        login_state = client.login(username=user.username, password='12345')
        self.assertEqual(login_state, True)


class RegistrationTestCase(TestCase):

    def test_register_post(self):
        input_data = {'username': 'DevTest',
                      'password_first': '12345',
                      'password_second': '12345',
                      'company_name': '1000Geeks',
                      'address': 'USA',
                      'first_email': 'test@gmail.com',
                      'second_email': 'test@yandex.by',
                      'phone': '+43423453',
                      'industry': 'Da',
                      'website': '+'}

        form = forms.RegisterForm(data=input_data)
        self.failUnless(form.is_valid())


