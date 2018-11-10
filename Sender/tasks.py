from __future__ import absolute_import, unicode_literals
from datetime import timedelta
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.core.cache import cache
from MessageSender.celery import app


@app.task(name="message_send")
def mass_send_mails(source_mail, target_mails, subject, text, link=None):
    send_mail(
        subject=subject,
        from_email=source_mail,
        recipient_list=[target_mails],
        fail_silently=False,
        html_message=render_to_string('mail_template.html', {'text': text, 'subject': subject, 'link': link}),
        message=text,
    )
