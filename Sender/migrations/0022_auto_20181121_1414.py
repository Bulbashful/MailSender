# Generated by Django 2.0.8 on 2018-11-21 14:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Sender', '0021_auto_20181121_0028'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useremails',
            name='mailer_second_email',
            field=models.EmailField(blank=True, max_length=100, null=True),
        ),
    ]
