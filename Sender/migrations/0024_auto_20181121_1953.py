# Generated by Django 2.0.8 on 2018-11-21 19:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Sender', '0023_auto_20181121_1445'),
    ]

    operations = [
        migrations.AddField(
            model_name='maileruser',
            name='mailer_account_type',
            field=models.CharField(choices=[('FREE', 'Free account'), ('PREM', 'Premium account')], default='FREE', max_length=4, verbose_name='account type'),
        ),
        migrations.AlterField(
            model_name='usermessage',
            name='user_message_sent_datetime',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
