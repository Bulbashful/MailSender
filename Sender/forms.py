from django import forms
from .models import *

from django_summernote.widgets import SummernoteWidget


# registration form
class RegisterForm(forms.Form):
    # username
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Login'}), label='Login')
    # password
    password_first = forms.CharField(widget=forms.PasswordInput(attrs={'minlength': 12,
                                                                       'placeholder':
                                                                           'Password - at least 12 characters'}),
                                     label='Password')
    # confirmation password
    password_second = forms.CharField(widget=forms.PasswordInput(attrs={'minlength': 12,
                                                                        'placeholder': 'Repeat the password'}),
                                      label='Confirm password')
    # company name
    company_name = forms.CharField(widget=forms.TextInput, label='Company name')
    # company address
    address = forms.CharField(widget=forms.TextInput, label='Address')
    # first email
    first_email = forms.EmailField(label='E-mail', widget=forms.EmailInput(attrs={
        'placeholder': 'E-mail (your company domain)'}))
    # second email
    second_email = forms.EmailField(label='Second e-mail', widget=forms.EmailInput(attrs={
        'placeholder': 'Second e-mail (your company domain)'}))
    # contact number
    phone = forms.CharField(widget=forms.TextInput, label='Contact number')
    # industry
    industry = forms.CharField(widget=forms.TextInput, label='Industry')
    # company website
    website = forms.CharField(widget=forms.TextInput, label='Website')


