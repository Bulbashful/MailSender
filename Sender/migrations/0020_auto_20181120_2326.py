# Generated by Django 2.1.3 on 2018-11-20 23:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('taggit', '0002_auto_20150616_2121'),
        ('Sender', '0019_auto_20181120_2258'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserMessage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_message_name', models.EmailField(max_length=100)),
                ('user_message_description', models.EmailField(max_length=500)),
                ('user_message_target_email', models.EmailField(max_length=100)),
                ('user_message_email_title', models.CharField(default='Mail from mailsender', max_length=50)),
                ('user_message_text', models.CharField(max_length=500)),
                ('user_message_sent_status', models.BooleanField(default=False)),
                ('user_message_sent_datetime', models.DateTimeField(default=django.utils.timezone.now)),
                ('user', models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='user_messages', to=settings.AUTH_USER_MODEL)),
                ('user_message_tags', taggit.managers.TaggableManager(blank=True, help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags')),
            ],
        ),
        migrations.RemoveField(
            model_name='usermessages',
            name='user',
        ),
        migrations.DeleteModel(
            name='UserMessages',
        ),
    ]