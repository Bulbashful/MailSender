# Generated by Django 2.1.3 on 2018-11-20 20:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0009_alter_user_last_name_max_length'),
        ('Sender', '0012_useremails_mailer_with_single_email'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserEmailMessages',
            fields=[
                ('user', models.OneToOneField(default=0, on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='user_messages', serialize=False, to=settings.AUTH_USER_MODEL)),
                ('target_email', models.EmailField(max_length=100)),
                ('text', models.CharField(max_length=256)),
                ('sent_status', models.BooleanField(default=False)),
            ],
        ),
    ]