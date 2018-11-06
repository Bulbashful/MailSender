from __future__ import absolute_import, unicode_literals

from django.core.mail import send_mail

from MessageSender.celery import app

'''
Для запуска нужно ввести из папки "MessageSender/":
celery -A MessageSender worker -l info
'''


# Messages sender worker
@app.task
def celery_send_mail(source_mail, target_mails, subject: str, text: str):
    send_mail(
        subject = subject,
        message = f"""{text}""",
        from_email = source_mail,
        recipient_list = [target_mails],
        fail_silently = False,
    )
