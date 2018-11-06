from django import forms
from .models import *

from django_summernote.widgets import SummernoteWidget


# форма для роегистрации нового пользователя
class RegisterForm(forms.Form):
    pass