# Generated by Django 2.0.8 on 2018-11-21 20:30

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Sender', '0025_auto_20181121_2016'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Сampaigns',
            new_name='Campaigns',
        ),
    ]