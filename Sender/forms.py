from django import forms

from django_summernote.widgets import SummernoteWidget


# registration form
class RegisterForm(forms.Form):
    # username
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username',
                                                             'class': 'form-control form-control-sm'}), label='Username')
    # password
    password_first = forms.CharField(widget=forms.PasswordInput(attrs={'minlength': 8,
                                                                       'placeholder':
                                                                           'Password - at least 8 characters',
                                                                       'class': 'form-control form-control-sm'}),
                                     label='Password')
    # confirmation password
    password_second = forms.CharField(widget=forms.PasswordInput(attrs={'minlength': 8,
                                                                        'placeholder': 'Repeat the password',
                                                                        'class': 'form-control form-control-sm'},),
                                      label='Confirm password')
    # company name
    company_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control form-control-sm',
                                                                 'placeholder': 'Company name'}),
                                   label='Company name',)
    # company address
    address = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control form-control-sm',
                                                            'placeholder': 'Address'}),
                              label='Address')
    # first email
    first_email = forms.EmailField(label='E-mail', widget=forms.EmailInput(attrs={'placeholder': 'E-mail (your company domain)',
                                                                                  'class': 'form-control form-control-sm'}))

    # second email
    second_email = forms.EmailField(label='Second e-mail', widget=forms.EmailInput(attrs={
        'placeholder': 'Second e-mail (your company domain)',
        'class': 'form-control form-control-sm'}), required=False)
    # contact number
    phone = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control form-control-sm',
                                                          'placeholder': 'Contact number'}),
                            label='Contact number')
    # industry
    industry = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control form-control-sm',
                                                             'placeholder': 'Industry'}),
                               label='Industry')
    # company website
    website = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control form-control-sm',
                                                            'placeholder': 'Website'}),
                              label='Website')


class ChangeUserInfo(forms.Form):
    mailer_user = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username',
                                                             'class': 'form-control form-control-sm'}),
                               label='Username')
    # company name
    mailer_company = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control form-control-sm',
                                                                 'placeholder': 'Company name'}),
                                   label='Company name')
    # company address
    mailer_company_address = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control form-control-sm',
                                                            'placeholder': 'Address'}),
                              label='Address')
    # first email
    mailer_first_email = forms.EmailField(label='E-mail', widget=forms.EmailInput(attrs={
        'placeholder': 'E-mail (your company domain)',
        'class': 'form-control form-control-sm'}))
    # second email
    mailer_second_email = forms.EmailField(label='Second e-mail', widget=forms.EmailInput(attrs={
        'placeholder': 'Second e-mail (your company domain)',
        'class': 'form-control form-control-sm'}), required=False)
    # contact number
    mailer_phone_number = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control form-control-sm',
                                                          'placeholder': 'Contact number'}),
                            label='Contact number')
    # industry
    mailer_company_industry = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control form-control-sm',
                                                             'placeholder': 'Industry'}),
                               label='Industry')
    # company website
    mailer_company_website = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control form-control-sm',
                                                            'placeholder': 'Website'}),
                              label='Website')


# login form
class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username',
                                                             'class': 'form-control form-control-sm'}), label='Username')
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password',
                                                                 'class': 'form-control form-control-sm'}), label='Password')


class PasswordRecoveryForm(forms.Form):
    # email to send new password
    email = forms.EmailField(label='E-mail', widget=forms.EmailInput(attrs={
        'placeholder': 'Enter your email to recovery password',
        'class': 'form-control form-control-sm'}))


class ChangePasswordForm(forms.Form):
    # email to send new password
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Old password',
                                                                     'class': 'form-control form-control-sm'}))
    new_password = forms.CharField(widget=forms.PasswordInput(attrs={'minlength': 8,
                                                                     'placeholder':'New password - at least 8 characters',
                                                                     'class': 'form-control form-control-sm'}),)


class CampaignForm(forms.Form):
    campaign_name = forms.CharField(label='Second e-mail', max_length=500, widget=forms.TextInput(attrs={
                                                                                                'placeholder': 'Campaign name',
                                                                                                'class': 'form-control',
                                                                                               }))
    campaign_description = forms.CharField(label='Second e-mail', max_length=500, widget=forms.Textarea(attrs={
                                                                                                'placeholder': 'Campaign description',
                                                                                                'class': 'form-control',
                                                                                               }))
    campaign_tags = forms.CharField(label='Second e-mail', max_length=50, widget=forms.TextInput(attrs={
                                                                                                'placeholder': 'Campaign tags',
                                                                                                'class': 'form-control',
                                                                                               }))                                                                                                                                                                                              
    # email to send message
    campaign_target_email = forms.EmailField(label='E-mail', widget=forms.EmailInput(attrs={
                                                                                    'placeholder': 'Enter user email',
                                                                                    'class': 'form-control form-control-sm'
                                                                                   }))
    campaign_email_title = forms.CharField(label='Title', max_length=50, widget=forms.TextInput(attrs={
                                                                                                'placeholder': 'Email title',
                                                                                                'class': 'form-control form-control-sm'
                                                                                                }))
    campaign_text = forms.CharField(label='Second e-mail', max_length=500, widget=forms.Textarea(attrs={
                                                                                                'placeholder': 'Email text',
                                                                                                'class': 'form-control',
                                                                                               }))

class CampaignsSearchForm(forms.Form):
    campaign_search = forms.CharField(label='Search', max_length=150, widget=forms.TextInput(attrs={
                                                                                                'placeholder': 'Search request',
                                                                                                'class': 'form-control'
                                                                                            }))
 