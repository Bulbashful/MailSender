"""
WSGI config for MessageSender project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/howto/deployment/wsgi/
"""

"""
On production
export DJANGO_SETTINGS_MODULE="MessageSender.production_settings"
====================================================================
On test
export DJANGO_SETTINGS_MODULE="MessageSender.settings"
"""
import os

from django.core.wsgi import get_wsgi_application

# On production
os.environ['DJANGO_SETTINGS_MODULE'] = 'MessageSender.production_settings'

# On test
#os.environ["DJANGO_SETTINGS_MODULE"] = "MessageSender.settings"

application = get_wsgi_application()
