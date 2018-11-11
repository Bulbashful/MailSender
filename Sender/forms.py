from django import forms
from .models import *

from django_summernote.widgets import SummernoteWidget


# registration form
class RegisterForm(forms.Form):
    # username
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username',
                                                             'class': 'form-control form-control-sm'}), label='Username')
    # password
    password_first = forms.CharField(widget=forms.PasswordInput(attrs={'minlength': 12,
                                                                       'placeholder':
                                                                           'Password - at least 12 characters',
                                                                       'class': 'form-control form-control-sm'}),
                                     label='Password')
    # confirmation password
    password_second = forms.CharField(widget=forms.PasswordInput(attrs={'minlength': 12,
                                                                        'placeholder': 'Repeat the password',
                                                                        'class': 'form-control form-control-sm'}),
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
    first_email = forms.EmailField(label='E-mail', widget=forms.EmailInput(attrs={
        'placeholder': 'E-mail (your company domain)',
        'class': 'form-control form-control-sm'}))
    # second email
    second_email = forms.EmailField(label='Second e-mail', widget=forms.EmailInput(attrs={
        'placeholder': 'Second e-mail (your company domain)',
        'class': 'form-control form-control-sm'}))
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
