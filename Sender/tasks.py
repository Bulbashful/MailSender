from __future__ import absolute_import, unicode_literals
from datetime import timedelta
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.core.cache import cache
from MessageSender.celery import app
from celery.result import AsyncResult

"""
to run celery use command : 
celery -A MessageSender worker -l info
"""


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

# По-ходу бред
@app.task
def check_result(task_id, message):
    task = AsyncResult(task_id)
    while True:
        if task.ready():
            message.sent_status = True
            message.save()
            break
