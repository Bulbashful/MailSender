# Generated by Django 2.0.8 on 2018-11-21 21:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Sender', '0026_auto_20181121_2030'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='usermessage',
            options={'verbose_name_plural': 'Users Campaigns'},
        ),
        migrations.RenameField(
            model_name='usermessage',
            old_name='user_message_description',
            new_name='campaign_description',
        ),
        migrations.RenameField(
            model_name='usermessage',
            old_name='user_message_email_title',
            new_name='campaign_email_title',
        ),
        migrations.RenameField(
            model_name='usermessage',
            old_name='user_message_name',
            new_name='campaign_name',
        ),
        migrations.RenameField(
            model_name='usermessage',
            old_name='user_message_sent_datetime',
            new_name='campaign_sent_datetime',
        ),
        migrations.RenameField(
            model_name='usermessage',
            old_name='user_message_sent_status',
            new_name='campaign_sent_status',
        ),
        migrations.RenameField(
            model_name='usermessage',
            old_name='user_message_tags',
            new_name='campaign_tags',
        ),
        migrations.RenameField(
            model_name='usermessage',
            old_name='user_message_target_email',
            new_name='campaign_target_email',
        ),
        migrations.RenameField(
            model_name='usermessage',
            old_name='user_message_text',
            new_name='campaign_text',
        ),
    ]