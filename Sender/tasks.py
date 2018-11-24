from __future__ import absolute_import, unicode_literals
from datetime import timedelta

from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.core.cache import cache

from MessageSender.celery import app
from celery.result import AsyncResult

from .models import UserSavedCampaigns, User, AttachedFiles

"""
to run celery use command : 
celery -A MessageSender worker -l info
"""


@app.task(name="message_send")
def mass_send_mails(source_mail, target_mails, subject, text, host, link=None):
    
    mail_template_payload = {
        'message_type': 'system',
        'text': text,
        'subject': subject,
        'link': link,
        'host': f'http://{host}'
    }

    send_mail(
        subject=subject,
        from_email=settings.EMAIL_HOST_USER if not source_mail else source_mail,
        recipient_list=[target_mails],
        fail_silently=False,
        html_message=render_to_string('mail_template.html', mail_template_payload),
        message=text,
    )


@app.task(name="user_message_send")
def user_send_mail(target_mail, subject, campaign_description, campaign_name, campaign_id, host, message_id):
    """
    Function send user email from servece to target

    :param target_mail: Target user mail
    :param subject: Email subject
    :param text: Email text
    :param message_id: User created message id
    """
    # get message object by id 
    saved_message = UserSavedCampaigns.objects.get(id=message_id)
    
    # get files for campaign
    campaign_files = AttachedFiles.objects.filter(campaign__id=campaign_id)
    try:
        mail_template_payload = {
            'message_type': 'save_company',
            'campaign_description': campaign_description,
            'subject': subject,
            'campaign_name': campaign_name,
            'campaign_files': campaign_files,
            'host': f'http://{host}'
        }
        send_mail(
            subject=subject,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[target_mail],
            fail_silently=False,
            html_message=render_to_string('mail_template.html', mail_template_payload),
            message=campaign_description,
        )
        # after success sending - change `campaign_sent_status` to True
        saved_message.saved_campaign_sent_status = True
        saved_message.save()
    
    except Exception as err:
        print(err)
