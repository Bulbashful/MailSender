# Generated by Django 2.0.8 on 2018-11-23 00:30

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('Sender', '0037_auto_20181123_0027'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usersavedcampaigns',
            name='saved_campaign_sent_datetime',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]