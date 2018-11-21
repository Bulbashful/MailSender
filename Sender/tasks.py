from __future__ import absolute_import, unicode_literals
from datetime import timedelta

from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.core.cache import cache

from MessageSender.celery import app
from celery.result import AsyncResult

from .models import UserMessage, User

"""
to run celery use command : 
celery -A MessageSender worker -l info
"""


@app.task(name="message_send")
def mass_send_mails(source_mail, target_mails, subject, text, link=None):
    send_mail(
        subject=subject,
        from_email=settings.EMAIL_HOST_USER if not source_mail else source_mail,
        recipient_list=[target_mails],
        fail_silently=False,
        html_message=render_to_string('mail_template.html', {'text': text, 'subject': subject, 'link': link}),
        message=text,
    )


@app.task(name="user_message_send")
def user_send_mail(target_mail, subject, text, message_id):
    """
    Function send user email from servece to target

    :param target_mail: Target user mail
    :param subject: Email subject
    :param text: Email text
    :param message_id: User created message id
    """
    # get message object by id 
    message = UserMessage.objects.get(id=message_id)
    
    try:
        send_mail(
            subject=subject,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[target_mail],
            fail_silently=False,
            html_message=render_to_string('mail_template.html', {'text': text, 'subject': subject,}),
            message=text,
        )
        # after success sending - change `user_message_sent_status` to True
        message.user_message_sent_status = True
        message.save()
    
    except Exception as err:
        print(err)
