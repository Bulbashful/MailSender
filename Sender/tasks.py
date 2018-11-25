from __future__ import absolute_import, unicode_literals
import os
from datetime import timedelta

from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from django.core.cache import cache

from MessageSender.celery import app
from celery.result import AsyncResult

from .models import UserSavedCampaigns, User, AttachedFiles, Campaign

"""
to run celery use command : 
celery -A MessageSender worker -l info
"""


@app.task(name="message_send")
def mass_send_mails(target_mails, subject, text, host, link=None):
    """
    Function send system messages
    
    :param target_mails: List of target mails to send system message
    :param subject: Mail subject
    :param text: Mail text
    :param host: Project host
    """
    
    mail_template_payload = {
        'message_type': 'system',
        'text': text,
        'subject': subject,
        'link': link,
        'host': f'http://{host}'
    }

    send_mail(
        subject=subject,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[target_mails],
        fail_silently=False,
        html_message=render_to_string('mail_template.html', mail_template_payload),
        message=text,
    )


@app.task(name="user_message_send")
def user_send_mail(target_mail, subject, campaign_id, host, message_id):
    """
    Function send user email with company description

    :param target_mail: Target user mail
    :param subject: Email subject
    :param campaign_id: Sended campaign id (get campaign files)
    :param host: Project host
    :param message_id: Message ID
    """
    # get message object by id 
    saved_message = UserSavedCampaigns.objects.get(id=message_id)
    # get campaign info 
    campaign = Campaign.objects.get(id=campaign_id)
    # get files for campaign
    campaign_files = AttachedFiles.objects.filter(campaign=campaign)
    try:
        # prepare template payload
        mail_template_payload = {
            'message_type': 'save_company',
            'campaign_description': campaign.campaign_description,
            'subject': subject,
            'campaign_name': campaign.campaign_name,
            'host': f'http://{host}'
        }
        #prepare email message
        mail_message = EmailMessage(
            subject=subject,
            body=render_to_string('mail_template.html', mail_template_payload),
            from_email=settings.EMAIL_HOST_USER,
            to=[target_mail]
        )
        mail_message.content_subtype = "html"

        for campaign_file in campaign_files:
            mail_message.attach(campaign_file.filename(), campaign_file.campaign_file.read())

        mail_message.send()

        # after success sending - change `campaign_sent_status` to True
        saved_message.saved_campaign_sent_status = True
        saved_message.save()
    
    except Exception as err:
        print(err)
