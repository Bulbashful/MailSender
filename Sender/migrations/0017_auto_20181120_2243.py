# Generated by Django 2.1.3 on 2018-11-20 22:43

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Sender', '0016_auto_20181120_2118'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='UserEmailMessages',
            new_name='UserMessages',
        ),
    ]
