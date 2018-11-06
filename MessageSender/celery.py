from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MessageSender.settings')
app = Celery('MessageSender', broker='amqp://localhost:5672/', backend='rpc://')

app.config_from_object('django.conf:settings', namespace='CELERY')
# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
