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
from django.shortcuts import get_object_or_404
from django.db import IntegrityError

from .models import User, DomainBlackList, UserEmails, MailerUser
from .forms import RegisterForm, LoginForm, PasswordRecoveryForm, ChangeUserInfo

from .tasks import mass_send_mails


# home page
class HomePage(View):
    content = {}

    # get request
    def get(self, request):
        self.content.update({
            'doc': 'index.html',
            'title': 'Main',
        })
        return render(request, 'base.html', self.content)

    def post(self, request):
        pass


# home page
class AccountSettings(View):
    content = {}

    # return user object and init dict
    def get_user_with_init(self):
        user = self.request.user
        data = {'mailer_user': user.user_account.mailer_user,
                'mailer_company': user.user_account.mailer_company,
                'mailer_company_address': user.user_account.mailer_company_address,
                'mailer_first_email': user.user_emails.mailer_first_email,
                'mailer_second_email': user.user_emails.mailer_second_email,
                'mailer_phone_number': user.user_account.mailer_phone_number,
                'mailer_company_industry': user.user_account.mailer_company_industry,
                'mailer_company_website:': user.user_account.mailer_company_website}
        return user, data

    # function that check if username has changes
    def if_change_user(self, user, fields, changed_form):
        print(fields)
        if 'mailer_user' in fields:
            fields.remove('mailer_user')
            pass
        else:
            fields.remove('mailer_user')
            try:
                setattr(user, 'username', changed_form.cleaned_data['mailer_user'])
                user.save()
                return True
            except IntegrityError:
                pass

    # danger!
    def save_model_and_send_email(self, user, changed_form, fields, email_num=None):
        if email_num is not None:
            if not self.if_change_user(user, fields, changed_form):
                messages.add_message(self.request, messages.WARNING,
                                     "Username already exists")
                return redirect('account-settings')
            [setattr(user.user_account if attr != email_num else
                     user.user_emails, attr, changed_form.cleaned_data[attr]) for attr in fields]

            # set account as non active
            setattr(user.user_emails, email_num + '_status', False)
            setattr(user.user_account, 'mailer_user_status', "NCN")
            setattr(user, 'is_active', False)

            user.user_emails.save()

            # new email that needed to be verified
            first_email = getattr(user.user_emails, email_num)
            # second user email to inform user about changed fields
            second_email = getattr(user.user_emails, 'mailer_first_email' if email_num == 'mailer_second_email' else
                                                                                                'mailer_second_email')

            # new hash
            link = f'http://{self.request.get_host()}/activation/{user.id}/' \
                          f'{hashlib.sha224(str(user.username + first_email).encode()).hexdigest()}'

            #TODO add str format according of fields
            fields = ' '.join(fields)

            # dict contains info about new email to send end info of changed info to send to second email
            emails = {'new_email_to_validate': [first_email, 'Confirm pls your email', 'Mail confirmation', link],
                      'second_email_with_info': [second_email, fields, 'Changed fields', None]}

            for email in emails:
                mass_send_mails.delay(
                    source_mail=settings.EMAIL_HOST_USER,
                    target_mails=emails[email][0],
                    text=emails[email][1],
                    subject=emails[email][2],
                    link=emails[email][3])

            logout(self.request)
        else:
            user_result = self.if_change_user(user, fields, changed_form)
            if not user_result:
                [setattr(user.user_account, attr, changed_form.cleaned_data[attr]) for attr in fields]
                try:
                    fields.remove('mailer_first_email')
                    fields.remove('mailer_second_email')
                except ValueError:
                    pass

                fields.append('mailer_user') if user_result else None

                fields = ' '.join(fields)
                mass_send_mails.delay(
                    source_mail=settings.EMAIL_HOST_USER,
                    target_mails=user.user_emails.mailer_first_email,
                    text=fields,
                subject='Changed fields')

        user.user_account.save()

    def get(self, request):
        user, data = self.get_user_with_init()
        self.content.update({
            'doc': 'user_account.html',
            'title': 'Account Settings',
            'change_info_form': ChangeUserInfo(initial=data)
        })
        return render(request, 'base.html', self.content)

    def post(self, request):
        user, data = self.get_user_with_init()
        # parse registration form
        changed_form = ChangeUserInfo(request.POST, initial=data)
        if changed_form.has_changed() and changed_form.is_valid():
            fields = changed_form.changed_data
            print(fields)
            if 'mailer_first_email' in fields and 'mailer_second_email' in fields:
                messages.add_message(request, messages.WARNING,
                                     "You can change only one email")
                self.save_model_and_send_email(user, changed_form, fields)
            elif 'mailer_first_email' in fields:
                self.save_model_and_send_email(user, changed_form, fields, 'mailer_first_email')
            elif 'mailer_second_email' in fields:
                self.save_model_and_send_email(user, changed_form, fields, 'mailer_second_email')
            else:
                self.save_model_and_send_email(user, changed_form, fields)
            return redirect('account-settings')
        else:
            print(changed_form.errors)
            print('not valid')
        return redirect('account-settings')


# mail verification
class MailVerify(View):
    content = {}

    def get(self, request, id, activation_string):
        try:
            # user instance
            user = User.objects.get(id=id)
            # user email instance
            email = UserEmails.objects.get(user=user)

            # first email address
            first_email = email.mailer_first_email
            # first email address status
            first_email_status = email.mailer_first_email_status
            # second email address
            second_email = email.mailer_second_email
            # second  email address status
            second_email_status = email.mailer_second_email_status

            # hash stings according user's emails
            first_user_account_hash = hashlib.sha224(str(user.username + first_email).encode()).hexdigest()
            second_user_account_hash = hashlib.sha224(str(user.username + second_email).encode()).hexdigest()

            # call function that compare hash string and action code
            first_email_state = check_email(request, activation_string, first_user_account_hash, first_email_status, user)
            second_email_state = check_email(request, activation_string, second_user_account_hash, second_email_status, user)

            # verify user email according of check_email() result
            if first_email_state:
                email.mailer_first_email_status = True
            elif second_email_state:
                email.mailer_second_email_status = True
            # if user trying verify verified email
            else:
                messages.add_message(request, messages.WARNING, 'Your email confirmed already')

            # compares if emails verified. If true user setting is active and mailer user is setting 'emails
            # confirmed status
            if email.mailer_first_email_status and email.mailer_second_email_status:
                mailer_user = MailerUser.objects.get(mailer_user=user)
                mailer_user.mailer_user_status = mailer_user.mail_confirmed_user
                user.is_active = True
                user.save()
                mailer_user.save()
                messages.add_message(request, messages.INFO, 'Your emails confirmed successfully')
            email.save()
        except:
            messages.add_message(request, messages.ERROR, 'Error while account activation')

        finally:
            return redirect('home')


# login page
class LoginPage(View):
    content = {}

    # get request
    def get(self, request):
        self.content.update({
            'doc': 'forms/login.html',
            'title': 'login',
            'login_form': LoginForm(),
        })
        return render(request, 'base.html', self.content)

    def post(self, request):
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            # try to find user and 404 if user not found
            user = get_object_or_404(User, username=login_form.cleaned_data['username'])
            # check password from user form to user instance
            if user.check_password(login_form.cleaned_data['password']):
                # check if verified emails
                if not user.is_active:
                    messages.add_message(request, messages.ERROR, 'Your emails does not verified yet')
                # check account status
                elif user.user_account.mailer_user_status != MailerUser.admin_confirmed_user:
                    messages.add_message(request, messages.ERROR, "Admin don't verified your account yet")
                # login if all ok
                else:
                    login(request, user)
                    return redirect('home')
            else:
                messages.add_message(request, messages.ERROR, 'Invalid username or password')
        else:
            messages.add_message(request, messages.ERROR, 'Error in login attempt')
        return redirect('login')


# logout view
class Logout(View):
    content = {}

    def get(self, request):
        logout(request)
        messages.add_message(request, messages.SUCCESS, 'LogOut completed successfully!')
        return redirect('home')


# registration page
class RegistrationPage(View):
    content = {}

    def get(self, request):
        self.content.update({
            'doc': 'forms/registration.html',
            'title': 'Registration',
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
                # create not verified mailer_user
                mailer_user = MailerUser.objects.create(mailer_user=new_user,
                                                        mailer_company=register_form.cleaned_data['company_name'],
                                                        mailer_company_address=register_form.cleaned_data['address'],
                                                        mailer_phone_number=register_form.cleaned_data['phone'],
                                                        mailer_company_industry=register_form.cleaned_data['industry'],
                                                        mailer_company_website=register_form.cleaned_data['website'])
                # create user's emails
                user_emails = UserEmails.objects.create(user=new_user,
                                                        mailer_first_email=register_form.cleaned_data['first_email'],
                                                        mailer_second_email=register_form.cleaned_data['second_email'])

                first_link = f'http://{request.get_host()}/activation/{new_user.id}/' \
                    f'{hashlib.sha224(str(new_user.username + user_emails.mailer_first_email).encode()).hexdigest()}'
                second_link = f'http://{request.get_host()}/activation/{new_user.id}/' \
                    f'{hashlib.sha224(str(new_user.username + user_emails.mailer_second_email).encode()).hexdigest()}'

                # create activation links dictionary. Key - emails, value - activation link
                links = {}
                links.update({
                    user_emails.mailer_first_email: first_link,
                    user_emails.mailer_second_email: second_link,
                })
                mailer_user.save()
                user_emails.save()

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
            messages.add_message(request, messages.ERROR, "Can't create account, check your form and password valid")
        return redirect('registration')


# password recovery page
class PasswordRecovery(View):
    content = {}

    # get request
    def get(self, request):
        self.content.update({
            'doc': 'forms/reset_password.html',
            'title': 'Password recovery',
            'reset_password_form': PasswordRecoveryForm(),
        })
        return render(request, 'base.html', self.content)

    def post(self, request):
        form = PasswordRecoveryForm(request.POST)
        if form.is_valid():
            target_mail = form.cleaned_data['email']
            # call function to create password
            new_password = random_password()
            try:
                # searching and setting new password for user
                user = UserEmails.objects.get(mailer_first_email=target_mail).user
                user.set_password(new_password)
                user.save()

                mass_send_mails.delay(target_mails=(target_mail),
                                      source_mail=settings.EMAIL_HOST_USER,
                                      text=f'Your new Password : {new_password}',
                                      subject='Change password.')

                messages.add_message(request, messages.WARNING, "Password changed! Log in now please.")
                return redirect('home')

            except ObjectDoesNotExist:
                messages.add_message(request, messages.WARNING, "Email not found!")
        else:
            messages.add_message(request, messages.WARNING, "Invalid form data")
        return redirect('password_reset')


# check identity password and that emails are various
def check_registration_credentials(password_first, password_second, first_email, second_email):
    # check password on identity
    password_state = password_first == password_second
    # check email on identity
    email_state = first_email != second_email
    return password_state and email_state


# function that check activation code and user email hash, email status and user state
def check_email(request, activation_string, user_account_hash, email_status, user):
    if activation_string == user_account_hash and not email_status and not user.is_active:
        messages.add_message(request, messages.INFO, 'Your email confirmed successfully')
        return True


# function that creation new password
def random_password():
    random.seed()
    random_pass = string.ascii_lowercase[random.randint(10, 12):-random.randint(10, 12)] \
                  + string.ascii_uppercase[random.randint(10, 15):-random.randint(10, 12)] \
                  + string.ascii_lowercase[random.randint(10, 12):-random.randint(10, 12)] \
                  + string.ascii_uppercase[random.randint(10, 12):-random.randint(10, 12)] \
                  + string.ascii_lowercase[random.randint(10, 12):-random.randint(10, 14)] \
                  + string.ascii_uppercase[random.randint(10, 14):-random.randint(10, 14)] \
                  + string.ascii_lowercase[random.randint(10, 14):-random.randint(10, 14)] \
                  + string.digits[1:random.randint(2, 8)]
    return random_pass