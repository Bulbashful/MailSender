import random
import string
import re
import hashlib
from datetime import datetime

from django.db.models import Sum
from django.shortcuts import render
from django.views import View
from django.contrib import messages
from django.shortcuts import redirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import logout, login, authenticate
from django.conf import settings
from django.db.models import Q
from django.db.models.query import QuerySet
from django.http import JsonResponse
from django.http import HttpResponseRedirect
from django.utils.timezone import now
from django.db import IntegrityError
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import User, DomainBlackList, UserEmails, MailerUser, Campaign, AttachedFiles, UserSavedCampaigns
from .forms import RegisterForm, LoginForm, PasswordRecoveryForm, ChangeUserInfo, ChangePasswordForm, CampaignForm, CampaignsSearchForm

from .tasks import mass_send_mails, user_send_mail


# home page
class HomePage(View):
    content = {}

    def get(self, request):
        self.content.update({
            'doc': 'index.html',
            'title': 'Main',
        })
        return render(request, 'base.html', self.content)

    def post(self, request):
        pass


# account settings page
class AccountSettings(LoginRequiredMixin, View):
    content = {}
    fields_format = {'mailer_user': 'Username',
                     'mailer_company': 'Company name',
                     'mailer_company_address': 'Company address',
                     'mailer_first_email': 'First email',
                     'mailer_second_email': 'Second email',
                     'mailer_phone_number': 'Contact number',
                     'mailer_company_industry': 'Company industry',
                     'mailer_company_website': 'Company website'}
    
    # redirect if not log in
    login_url = '/login/'                 
    redirect_field_name = 'login'

    # convert fields to present view for email
    def __present_string_format(self, fields: list):
        # make from changed fileds list - string separated by coma
        return ', '.join([self.fields_format[field] for field in fields])

    # return user object and init dict
    def __get_user_with_init(self):
        user = self.request.user
        data = {'mailer_user': user.username,
                'mailer_company': user.user_account.mailer_company,
                'mailer_company_address': user.user_account.mailer_company_address,
                'mailer_first_email': user.user_emails.mailer_first_email,
                'mailer_second_email': user.user_emails.mailer_second_email,
                'mailer_phone_number': user.user_account.mailer_phone_number,
                'mailer_company_industry': user.user_account.mailer_company_industry,
                'mailer_company_website': user.user_account.mailer_company_website}
        return user, data

    # function that check if username has changes, if new username exist and update it
    def __if_change_username(self, user, new_username: str):
        """
        Method get user(object), new_username(new username string). Check if new username already exist.
        If new username - unique, set it and save new user. Or create new message with ERROR.
        
        :param user: User base object
        :param new_username: New username string

        :return: None
        """
        new_username_used = User.objects.filter(username=new_username).first()
        
        if not new_username_used:
            user.username = new_username
                
            user.save()
            messages.add_message(self.request, messages.SUCCESS, "Username changed")
            
        # if user username already exist
        else:
            messages.add_message(self.request, messages.ERROR, "Username already exists")

    # save new model data and send notofications
    def save_model_and_send_email(self, user, changed_form, changed_fields: list, email_num: str = ''):
        # prepare fields change list for message
        changed_fields_string = self.__present_string_format(changed_fields)

        # if user change username
        if 'mailer_user' in changed_fields:
            self.__if_change_username(user, changed_form.cleaned_data['mailer_user'])
            changed_fields.remove('mailer_user')
                
        # case when form contain one email
        if email_num:
            # save user old email to inform him
            old_email = getattr(user.user_emails, email_num)
            # set new email from change list
            user.user_emails.email_num = changed_form.cleaned_data[email_num]
            # delete this email from change list
            changed_fields.remove(email_num)

            [setattr(user.user_account, changed_attr, changed_form.cleaned_data[changed_attr]) for changed_attr in changed_fields]

            # set new user email
            setattr(user.user_emails, email_num, changed_form.cleaned_data[email_num])
            # set Сampaigns user changed mail status as not activated
            setattr(user.user_emails, email_num + '_status', False)

            # new hash
            link = f'/activation/{user.id}/' \
                          f'{hashlib.sha224(str(user.username + changed_form.cleaned_data[email_num]).encode()).hexdigest()}'

            # dict contains info about new email to send and info of changed to send it to old email
            emails = {'new_email_to_validate': [
                                                    changed_form.cleaned_data[email_num], 
                                                    'Confirm please your email', 
                                                    'Mail confirmation', 
                                                    link
                                                ],
                      'old_email_with_info': [
                                                    old_email, 
                                                    f'Changed: {changed_fields_string};', 
                                                    'Changed fields', 
                                                    None
                                                ]
                    }
            # if user delete second mail
            if not changed_form.cleaned_data[email_num] and email_num=='mailer_second_email':
                # delete new email key
                del emails['new_email_to_validate']
                # set user_emails status mailer_with_single_email to True
                user.user_emails.mailer_with_single_email = True
                # set user second mail status to False
                user.user_emails.mailer_second_email_status = False

            # if user add mailer_second_email
            elif user.user_emails.mailer_with_single_email:
                del emails['old_email_with_info']
                user.user_emails.mailer_with_single_email = False
                # set MailerUser user mailer_user_status as `Not confirmed mail`
                setattr(user.user_account, 'mailer_user_status', MailerUser.not_confirmed_user)
                # set User user status as `is_active=False`
                setattr(user, 'is_active', False)
            # if user change mail
            else:
                # set MailerUser user mailer_user_status as `Not confirmed mail`
                setattr(user.user_account, 'mailer_user_status', MailerUser.not_confirmed_user)
                # set User user status as `is_active=False`
                setattr(user, 'is_active', False)


            #return redirect('account-settings')
            for email in emails:
                mass_send_mails.delay(
                    target_mails=emails[email][0],
                    text=emails[email][1],
                    subject=emails[email][2],
                    link=emails[email][3],
                    host=self.request.get_host())
            
            logout(self.request)
        # case when form contains two emails or none
        else:
            # update user data
            [setattr(user.user_account, changed_attr, changed_form.cleaned_data[changed_attr]) for changed_attr in changed_fields]

            mass_send_mails.delay(
                target_mails=user.user_emails.mailer_first_email,
                text=f'Changed: {changed_fields_string};',
                subject='Change some fields',
                host=self.request.get_host())

        # save new data
        user.save()
        user.user_emails.save()
        user.user_account.save()

        return redirect('account-settings')

    def get(self, request):
        user, data = self.__get_user_with_init()
        self.content.update({
            'doc': 'user_account.html',
            'title': 'Account Settings',
            'change_info_form': ChangeUserInfo(initial=data)
        })
        return render(request, 'base.html', self.content)

    def post(self, request):
        user, data = self.__get_user_with_init()
        # parse registration form
        changed_form = ChangeUserInfo(request.POST, initial=data)

        # check user emails (they must be not similar and not contain domains from `DomainBlackList`)
        email_check_result = check_registration_credentials(request, 
                                                            password_first='',
                                                            password_second='',
                                                            first_email = request.POST['mailer_first_email'],
                                                            second_email = request.POST.get('mailer_second_email'))

        if changed_form.has_changed() and changed_form.is_valid() and email_check_result:
            # get list of changed fields
            changed_fields = changed_form.changed_data
            
            if 'mailer_first_email' in changed_fields or 'mailer_second_email' in changed_fields:
                if 'mailer_first_email' in changed_fields:
                    self.save_model_and_send_email(user, changed_form, changed_fields, 'mailer_first_email')
                
                if 'mailer_second_email' in changed_fields:
                    self.save_model_and_send_email(user, changed_form, changed_fields, 'mailer_second_email')
                
            else:
                self.save_model_and_send_email(user, changed_form, changed_fields)
                
            messages.add_message(request, messages.SUCCESS, "Form successfully changed")
        else:
            messages.add_message(request, messages.ERROR, "Form not changed")

        return redirect('account-settings')


# change password page
class ChangePassword(LoginRequiredMixin, View):
    content = {}

    # redirect if not log in
    login_url = '/login/'                 
    redirect_field_name = 'login'

    def get(self, request):
        self.content.update({
            'doc': 'forms/change_password.html',
            'change_password_form': ChangePasswordForm(),
            'title': 'Change password',
        })
        return render(request, 'base.html', self.content)

    def post(self, request):
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            # check user old password
            old_password = self.request.user.check_password(form.cleaned_data['old_password'])
            # if old password is true
            if old_password:
                # set new password
                self.request.user.set_password(form.cleaned_data['new_password'])
                # save user profile
                self.request.user.save()
                # send mail notification
                mass_send_mails.delay(target_mails=self.request.user.user_emails.mailer_first_email,                                      
                                      text=f'Password has changed successfully',
                                      subject='Change password.',
                                      host=self.request.get_host())
                
                messages.add_message(request, messages.SUCCESS, "Password changed!")
            else:
                messages.add_message(request, messages.ERROR, "Invalid old password!")
        else:
            messages.add_message(request, messages.WARNING, "Invalid form data or you didn't confirm your email")
        return redirect('change-password')


# detail campaign view
class CampaignDetailView(LoginRequiredMixin, View):
    content = {}

    # redirect if not log in
    login_url = '/login/'                 
    redirect_field_name = 'login'

    def get(self, request, campaign_id: int):
        campaign = Campaign.objects.get(id=campaign_id)
        self.content.update({
            'doc': 'campaigns_detail_view.html',
            'title': f'{campaign.campaign_name}',
        })
        self.content.update({'campaign': campaign,
                             'campaign_files': AttachedFiles.objects.filter(campaign=campaign)})

        return render(request, 'base.html', self.content)

    def post(self, request, campaign_id: int):
        # if user send campaign himself
        if 'send' in request.POST:            
            try:
                # get saved campaign by campaign ID
                saved_campaign, created = UserSavedCampaigns.objects.get_or_create(user=self.request.user,
                                                                                   saved_campaign_id=campaign_id)

                if not created:
                    saved_campaign.saved_campaign_sent_datetime = datetime.now()

                    saved_campaign.save()

                # send user mail
                user_send_mail.delay(target_mail=self.request.user.user_emails.mailer_first_email,
                                     campaign_id = campaign_id,
                                     host = request.get_host(),
                                     subject='Saved campaign',
                                     message_id=saved_campaign.id)

                messages.add_message(request, messages.SUCCESS, "Mail has been sent")
                
            except Exception as err:
                print(err)
                messages.add_message(request, messages.ERROR, f"Error while campaign save!")
        return redirect(f'/view-campaign/id-{campaign_id}')


# view with list of created campaigns
class CampaignsListView(LoginRequiredMixin, View):
    """
    List of Campaigns
    """
    content = {}

    # redirect if not log in
    login_url = '/login/'                 
    redirect_field_name = 'login'

    def get(self, request, tag: str = None):
        self.content.update({
            'doc': 'campaigns.html',
            'title': 'Campaigns',
            'search_form': CampaignsSearchForm()
        })

        all_campaigns = Campaign.objects.all()

        search_form = CampaignsSearchForm(request.GET)

        # if user set tag and search request
        if tag and search_form.is_valid():
            # filter campaigns by tag
            campaign_filtered_by_tag = all_campaigns.filter(campaign_tags__name__in = [tag])
            # get search request from form
            search_request = search_form.cleaned_data['campaign_search']

            # search data in Campaigns model
            searched_campaigns = self.__search(search_query = campaign_filtered_by_tag, 
                                               search_request = search_request)
            if searched_campaigns:
                messages.add_message(request, messages.SUCCESS, 'Success search')
            else:
                messages.add_message(request, messages.INFO, 'Nothing ...')

            self.content.update({'sended_messages': searched_campaigns})

        # if user send tag
        elif tag:
            campaign_filtered_by_tag = all_campaigns.filter(campaign_tags__name__in = [tag])

            self.content.update({'sended_messages': campaign_filtered_by_tag})

        # if user send search request
        elif search_form.is_valid():
            # get search request from form
            search_request = search_form.cleaned_data['campaign_search']

            # search data in Campaigns model
            searched_campaigns = self.__search(search_query = all_campaigns, 
                                               search_request = search_request)

            if searched_campaigns:
                messages.add_message(request, messages.SUCCESS, 'Success search')
            else:
                messages.add_message(request, messages.INFO, 'Nothing ...')

            self.content.update({'sended_messages': searched_campaigns})
        else:

            self.content.update({'sended_messages': all_campaigns})

        return render(request, 'base.html', self.content)

    def __search(self, search_query: QuerySet, search_request: str):
        # search by name
        search_campaign_by_name = search_query.filter(campaign_name__icontains = search_request)
        # search by description
        search_campaign_by_description = search_query.filter(campaign_description__icontains =search_request)
        
        searched_campaigns = search_campaign_by_name | search_campaign_by_description
            
        return searched_campaigns


# view with list of created campaigns
class SavedCampaignsListView(LoginRequiredMixin, View):
    """
    List of Campaigns
    """
    content = {}

    # redirect if not log in
    login_url = '/login/'                 
    redirect_field_name = 'login'

    def get(self, request, tag: str = None):
        self.content.update({
            'doc': 'saved_campaigns.html',
            'title': 'Campaigns',
            'search_form': CampaignsSearchForm()
        })

        all_campaigns_by_user = UserSavedCampaigns.objects.filter(user=request.user)

        search_form = CampaignsSearchForm(request.GET)

        # if user set tag and search request
        if tag and search_form.is_valid():
            # filter campaigns by tag
            campaign_filtered_by_tag = all_campaigns_by_user.filter(saved_campaign__campaign_tags__name__in = [tag])
            # get search request from form
            search_request = search_form.cleaned_data['campaign_search']

            # search data in Campaigns model
            searched_campaigns = self.__search(search_query = campaign_filtered_by_tag, 
                                               search_request = search_request)
            if searched_campaigns:
                messages.add_message(request, messages.SUCCESS, 'Success search')
            else:
                messages.add_message(request, messages.INFO, 'Nothing ...')

            self.content.update({'saved_campaigns': searched_campaigns})

        # if user send tag
        elif tag:
            campaign_filtered_by_tag = all_campaigns_by_user.filter(saved_campaign__campaign_tags__name__in = [tag])

            self.content.update({'saved_campaigns': campaign_filtered_by_tag})

        # if user send search request
        elif search_form.is_valid():
            # get search request from form
            search_request = search_form.cleaned_data['campaign_search']

            # search data in Campaigns model
            searched_campaigns = self.__search(search_query = all_campaigns_by_user, 
                                               search_request = search_request)

            if searched_campaigns:
                messages.add_message(request, messages.SUCCESS, 'Success search')
            else:
                messages.add_message(request, messages.INFO, 'Nothing ...')

            self.content.update({'saved_campaigns': searched_campaigns})
        else:

            self.content.update({'saved_campaigns': all_campaigns_by_user})

        return render(request, 'base.html', self.content)

    def __search(self, search_query: QuerySet, search_request: str):
        # search by name
        search_campaign_by_name = search_query.filter(saved_campaign__campaign_name__icontains = search_request)
        # search by description
        search_campaign_by_description = search_query.filter(saved_campaign__campaign_description__icontains =search_request)
        
        searched_campaigns = search_campaign_by_name | search_campaign_by_description
            
        return searched_campaigns


# mail verification
class MailVerify(View):
    content = {}

    def get(self, request, id, activation_string):
        try:
            # user instance
            user = User.objects.get(id=id)
            register_state = user.user_emails.mailer_with_single_email
            # case when user registered with two emails
            if not register_state:
                # first email address
                first_email = user.user_emails.mailer_first_email
                # first email address status
                first_email_status = user.user_emails.mailer_first_email_status
                # second email address
                second_email = user.user_emails.mailer_second_email
                # second  email address status
                second_email_status = user.user_emails.mailer_second_email_status

                # hash stings according user's emails
                first_user_account_hash = hashlib.sha224(str(user.username + first_email).encode()).hexdigest()
                second_user_account_hash = hashlib.sha224(str(user.username + second_email).encode()).hexdigest()

                # call function that compare hash string and action code
                first_email_state = check_email(request, activation_string, first_user_account_hash, first_email_status, user)
                second_email_state = check_email(request, activation_string, second_user_account_hash, second_email_status, user)

                # verify user email according of check_email() result
                if first_email_state:
                    user.user_emails.mailer_first_email_status = True
                elif second_email_state:
                    user.user_emails.mailer_second_email_status = True
                # if user trying verify verified email
                else:
                    messages.add_message(request, messages.WARNING, 'Your email confirmed already')

                # compares if emails verified. If true user setting is active and mailer user is setting 'emails
                # confirmed status
                if user.user_emails.mailer_first_email_status and user.user_emails.mailer_second_email_status:
                    mailer_user = MailerUser.objects.get(mailer_user=user)
                    mailer_user.mailer_user_status = mailer_user.mail_confirmed_user
                    user.is_active = True
                    user.save()
                    mailer_user.save()
                    messages.add_message(request, messages.SUCCESS, 'All your emails confirmed successfully')
                user.user_emails.save()
            # case when user registered with one email
            else:
                # first email address
                first_email = user.user_emails.mailer_first_email
                # first email address status
                first_email_status = user.user_emails.mailer_first_email_status
                # hash sting according user first  emails
                first_user_account_hash = hashlib.sha224(str(user.username + first_email).encode()).hexdigest()

                # call function that compare hash string and action code
                first_email_state = check_email(request, activation_string, first_user_account_hash, first_email_status,
                                                user)
                # verify user email according of check_email() result
                if first_email_state:
                    user.user_emails.mailer_first_email_status = True
                    user.user_account.mailer_user_status = "MCN"
                    user.is_active = True
                    user.user_emails.save()
                    user.user_account.save()
                    user.save()
                    messages.add_message(request, messages.SUCCESS, 'Your email confirmed successfully')
                # if user trying verify verified email
                else:
                    messages.add_message(request, messages.WARNING, 'Your email confirmed already')
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
            'title': 'Login',
            'login_form': LoginForm(),
        })
        return render(request, 'base.html', self.content)

    def post(self, request):
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            # try to find user in DB
            user = User.objects.filter(username=login_form.cleaned_data['username']).first()
            if user:
                # check password from user form to user instance
                if user.check_password(login_form.cleaned_data['password']):
                    # check if verified emails
                    if not user.is_active:
                        messages.add_message(request, messages.ERROR, 'Your email(s) does not verified yet. You need verifie 2(!!!) emails.')
                    # check account status
                    elif user.user_account.mailer_user_status != MailerUser.admin_confirmed_user:
                        messages.add_message(request, messages.ERROR, "Admin don't verified your account yet")
                    # login if all ok
                    else:
                        login(request, user)
                        return redirect('campaigns')
                else:
                    messages.add_message(request, messages.ERROR, 'Invalid username or password')
            else:
                messages.add_message(request, messages.ERROR, 'Error in login attempt')
        
        else:
            messages.add_message(request, messages.ERROR, 'Error in login form')
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

        if second_email == '':
            check_credentials = check_registration_credentials(request, password_first, password_second, first_email)
        else:
            check_credentials = check_registration_credentials(request, password_first, password_second, first_email,
                                                               second_email)

        if register_form.is_valid() and check_credentials:

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
                second_email = register_form.cleaned_data['second_email']

                user_emails = UserEmails.objects.create(user=new_user,
                                                        mailer_first_email=register_form.cleaned_data['first_email'],
                                                        mailer_second_email=second_email)

                # sorry; add true state if user register with one email
                user_emails.mailer_with_single_email = True if second_email == '' else False

                first_link = f'/activation/{new_user.id}/' \
                    f'{hashlib.sha224(str(new_user.username + user_emails.mailer_first_email).encode()).hexdigest()}'
                second_link = f'/activation/{new_user.id}/' \
                    f'{hashlib.sha224(str(new_user.username + user_emails.mailer_second_email).encode()).hexdigest()}'

                # create activation links dictionary. Key - emails, value - activation link
                links = {user_emails.mailer_first_email: first_link}
                # form contain second_email
                if second_email != '':
                    links.update({
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
                        target_mails=[link],
                        text='Confirm pls your email',
                        subject='Mail confirmation',
                        link=links[link],
                        host=self.request.get_host())

                messages.add_message(request, messages.SUCCESS, "You successfully registered! Check your mail!")
                return redirect('home')

            except Exception as err:
                print(err)
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
            # searching inserted emails
            emails_user = UserEmails.objects.filter(Q(mailer_first_email=target_mail) | Q(mailer_second_email=target_mail)).first()
            # if find emails - send new password
            if emails_user:

                # call function to create password
                new_password = random_password()
                # set new pass and save
                emails_user.user.set_password(new_password)
                emails_user.user.save()

                mass_send_mails.delay(target_mails=target_mail,
                                      text=f'Your new Password : {new_password}',
                                      subject='Change password.',
                                      host=self.request.get_host())

                messages.add_message(request, messages.WARNING, "Password changed! Log in now please.")
                return redirect('home')

            else:
                messages.add_message(request, messages.WARNING, "Email not found!")
        else:
            messages.add_message(request, messages.WARNING, "Invalid form data or you didn't confirm your email")
        return redirect('password_reset')


# check identity password and that emails are various
def check_registration_credentials(request, password_first: str, password_second: str, first_email: str,
                                   second_email: str=None):
    """
    Function check passwords(must be similar) and email(must be not similar and not contain domains from DomainBlackList)

    :param request: - view request
    :param password_first: - first inserted password
    :param password_second: - second inserted password
    :param first_email: - first inserted email
    :param second_email: - second inserted email

    :return: True(if all is Ok) or False(if some error happen)
    """
    # regexp pattern for mail domain checking
    get_domain_pattern = re.compile('@(\w+)')

    # check password on identity
    if password_first != password_second:
        messages.add_message(request, messages.WARNING, "Passwords not similar")
        return False
    # check emails on identity if function takes second_email
    if first_email and first_email == second_email:
            messages.add_message(request, messages.WARNING, "Email's are similar")
            return False

    # first_email_domain and  second_email_domain contains clear domain: gmail, yandex and etc.
    first_email_domain = get_domain_pattern.findall(first_email)
    # check second email if function takes it
    second_email_domain = get_domain_pattern.findall(second_email) if second_email else None
    # domain_result contain query result, if two email not in black list then domain_result is 0
    domain_result = DomainBlackList.objects.filter(Q(name=first_email_domain) | Q(name=second_email_domain)).first()

    if domain_result:
        messages.add_message(request, messages.ERROR,
                             "Can't create account, your e-mail does not meet the requirements")
        return False

    return True


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