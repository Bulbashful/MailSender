import random
import string
import re
import hashlib

from django.db.models import Sum
from django.shortcuts import render
from django.views import View
from django.contrib import messages
from django.shortcuts import redirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import logout, login, authenticate
from django.conf import settings
from django.db.models import Q
from django.http import JsonResponse
from django.http import HttpResponseRedirect
from django.utils.timezone import now


from .models import User, DomainBlackList, UserEmails, MailerUser
from .forms import RegisterForm

from .tasks import mass_send_mails


# home page
class HomePage(View):
    content = {}

    # get request
    def get(self, request):
        self.content.update({
            'doc': 'index.html',
        })
        return render(request, 'base.html', self.content)

    def post(self, request):
        pass


# home page
class MailVerify(View):
    content = {}

    def get(self, request, id, activation_string):
        try:
            user = User.objects.get(id=id)
            user_account_hash = hashlib.sha224(str(user).encode()).hexdigest()
            if activation_string == user_account_hash and not user.is_active:
                # TODO ---->
                """
                Check user mail as confirmed
                """

                messages.add_message(request, messages.SUCCESS, 'Success mail confirmation. Wait account activation.')
                return redirect('home')

            else:
                messages.add_message(request, messages.WARNING, 'Create new account firstly')

        except:
            messages.add_message(request, messages.ERROR, 'Error while account activation')

        finally:
            return redirect('home')


# login page
class LoginPage(View):
    content = {}

    # get request
    def get(self, request):
        pass

    def post(self, request):
        pass


# TODO правки
# registration page
class RegistrationPage(View):
    content = {}
    # black_list = ['gmail', 'outlook', 'icloud', 'yahoo', aol, gmx, zohom, protonmail, yandex, mail]

    def get(self, request):
        self.content.update({
            'doc': 'RLR/registration.html',
            'registration_form': RegisterForm(),
        })
        return render(request, 'base.html', self.content)

    def post(self, request):
        # parse registration form
        register_form = RegisterForm(request.POST)
        # password and emails fields from form
        password_first = request.POST['password_first']
        password_second = request.POST['password_second']
        first_email = request.POST['first_email']
        second_email = request.POST['second_email']
        # call function to check input part of data
        check_credentials = check_registration_credentials(password_first, password_second, first_email, second_email)
        if register_form.is_valid() and check_credentials:
            # regexp pattern
            get_domain_pattern = re.compile('@(\w+)')
            # first_email_domain and  second_email_domain contains clear domain: gmail, yandex and etc.
            first_email_domain = get_domain_pattern.findall(register_form.cleaned_data['first_email'])
            second_email_domain = get_domain_pattern.findall(register_form.cleaned_data['second_email'])
            # domain_result contain query result, if two email not it black list then domain_result is 0
            domain_result = DomainBlackList.objects.filter(Q(name=first_email_domain) | Q(name=second_email_domain))

            if len(domain_result) != 0:
                messages.add_message(request, messages.ERROR,
                                     "Can't create account, your e-mail does not meet the requirements")
                return redirect('registration')

            try:
                # create new user in DB with `is_active=False` param
                new_user = User.objects.create_user(username=register_form.cleaned_data['username'],
                                                    password=register_form.cleaned_data['password_first'],
                                                    is_active=False)
                # create user's emails
                user_emails = UserEmails.objects.create(mailer_first_email=register_form.cleaned_data['first_email'],
                                                        mailer_second_email=register_form.cleaned_data['second_email'])
                # create not verified mailer_user
                mailer_user = MailerUser.objects.create(mailer_user=new_user,
                                                        mailer_emails=user_emails,
                                                        mailer_company=register_form.cleaned_data['company_name'],
                                                        mailer_company_address=register_form.cleaned_data['address'],
                                                        mailer_phone_number=register_form.cleaned_data['phone'],
                                                        mailer_company_industry=register_form.cleaned_data['industry'],
                                                        mailer_company_website=register_form.cleaned_data['website'])

                # create activation links
                links = {}
                links.update({
                    user_emails.mailer_first_email: f'http://{request.get_host()}/activation/' \
                                    f'{new_user.id}/{hashlib.sha224(str(new_user.username + user_emails.mailer_first_email).encode()).hexdigest()}',
                    user_emails.mailer_second_email: f'http://{request.get_host()}/activation/' \
                                    f'{new_user.id}/{hashlib.sha224(str(new_user.username + user_emails.mailer_second_email).encode()).hexdigest()}'
                })
                user_emails.save()
                mailer_user.save()
                # TODO create message template
                """
                Note: Email would need to be confirmed, email verification. 
                      Anyone can register but pending admin approval. 
                """
                # send mail confirm message
                for link in links:
                    mass_send_mails.delay(
                        source_mail=settings.EMAIL_HOST_USER,
                        target_mails=[link],
                        text='Confirm pls your email',
                        subject='Mail confirmation',
                        link=links[link])

                messages.add_message(request, messages.SUCCESS, "You successfully registered! Check your mail!")
                return redirect('home')

            except:
                # if some error while user creation or message sending
                messages.add_message(request, messages.WARNING,
                                     "Can't create account, some error happened. Write to admins.")
        else:
            # при ошибке при заполнении формы
            messages.add_message(request, messages.ERROR, "Can't create account, check your form and password valid")
        return redirect('registration')


# password recovery page
class PasswordRecovery(View):
    content = {}

    # get request
    def get(self, request):
        pass

    def post(self, request):
        pass


def check_registration_credentials(password_first, password_second, first_email, second_email):
    # check password on identity
    password_state = password_first == password_second
    # check email on identity
    email_state = first_email != second_email
    return password_state and email_state
