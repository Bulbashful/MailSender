# Generated by Django 2.1.3 on 2018-11-10 11:57

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Sender', '0008_auto_20181110_1124'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useremails',
            name='mailer_user',
            field=models.OneToOneField(default=0, on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='user_emails', serialize=False, to=settings.AUTH_USER_MODEL),
        ),
    ]
