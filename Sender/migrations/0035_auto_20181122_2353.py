# Generated by Django 2.0.8 on 2018-11-22 23:53

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Sender', '0034_usersavedmessages'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserSavedCampaigns',
            fields=[
                ('saved_campaign', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='saved_campaign', serialize=False, to='Sender.Campaign')),
                ('saved_campaign_sent_status', models.BooleanField(default=False)),
                ('saved_campaign_sent_datetime', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='user_saved_messages', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Users Saved Campaigns',
            },
        ),
        migrations.RemoveField(
            model_name='usersavedmessages',
            name='saved_campaign',
        ),
        migrations.RemoveField(
            model_name='usersavedmessages',
            name='user',
        ),
        migrations.AlterModelOptions(
            name='campaign',
            options={'verbose_name_plural': 'Campaigns'},
        ),
        migrations.RemoveField(
            model_name='campaign',
            name='campaign_text',
        ),
        migrations.DeleteModel(
            name='UserSavedMessages',
        ),
    ]