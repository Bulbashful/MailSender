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


from .models import User
from .forms import RegisterForm

from .tasks import celery_send_mail


# home page
class HomePage(View):
    content = {}

    # get request
    def get(self, request):
        pass

    def post(self, request):
        pass


# home page
class AccountActivation(View):
    content = {}

    def get(self, request, id, activation_string):
        try:
            user = User.objects.get(id = id)
            user_account_hash = hashlib.sha224(str(user).encode()).hexdigest()
            if activation_string == user_account_hash and not user.is_active:
                # TODO сделать ---->
                """
                Помечать пользователя как подтвердившего почту, но аккаунт не активировать 
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


# registration page
class RegistrationPage(View):
    content = {}

    def get(self, request):
        self.content.update({
            'doc': 'pages/registration.html',
        })
        return render(request, 'base.html', self.content)

    def post(self, request):
        # parse registration form
        register_form = RegisterForm(request.POST)
        # password check
        if register_form.is_valid() and request.POST['password_first'] == request.POST['password_second']:

            # TODO Добавить проверку домена e-mail'a в блек-листе
            get_domain_pattern = re.compile('@(\w+)')
            domain_result = get_domain_pattern.findall(register_form.cleaned_data['email'])
            # domain_result будет содержать строку с чистым доменом, к прмиеру: gmail, yandex and etc.

            try:
                # create new user in DB with `is_active=False` param
                new_user = User.objects.create_user(username = register_form.cleaned_data['username'],
                                                    email = register_form.cleaned_data['email'],
                                                    password = register_form.cleaned_data['password_first'],
                                                    is_active = False)
                # create activation link
                activation_link = f'http://{request.get_host()}/activation/' \
                                  f'{new_user.id}/{hashlib.sha224(str(new_user).encode()).hexdigest()}'

                # TODO create message template
                """
                Note: Email would need to be confirmed, email verification. 
                      Anyone can register but pending admin approval. 
                """
                # send mail confirm message
                celery_send_mail.delay(
                    source_mail = settings.EMAIL_HOST_USER,
                    target_mails = [new_user.email],
                    text = f''' <MESSAGE_TEMPLATE> '''+activation_link,
                    subject = 'Mail confirmation')

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
