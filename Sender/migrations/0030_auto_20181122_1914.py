# Generated by Django 2.0.8 on 2018-11-22 19:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Sender', '0029_auto_20181121_2121'),
    ]

    operations = [
        migrations.CreateModel(
            name='AttachedFiles',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='attached_files')),
            ],
        ),
        migrations.RemoveField(
            model_name='campaign',
            name='campaign_email_title',
        ),
        migrations.RemoveField(
            model_name='campaign',
            name='campaign_sent_datetime',
        ),
        migrations.RemoveField(
            model_name='campaign',
            name='campaign_sent_status',
        ),
        migrations.RemoveField(
            model_name='campaign',
            name='campaign_target_email',
        ),
        migrations.RemoveField(
            model_name='campaign',
            name='user',
        ),
        migrations.AddField(
            model_name='campaign',
            name='attached_files',
            field=models.ForeignKey(default='1', on_delete=django.db.models.deletion.CASCADE, related_name='campaign_files', to='Sender.AttachedFiles'),
        ),
    ]