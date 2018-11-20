# Generated by Django 2.1.3 on 2018-11-20 20:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Sender', '0013_useremailmessages'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useremailmessages',
            name='user',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='user_messages', serialize=False, to=settings.AUTH_USER_MODEL),
        ),
    ]
