# Generated by Django 2.0.8 on 2018-11-24 00:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Sender', '0040_auto_20181123_0043'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='attachedfiles',
            options={'verbose_name_plural': 'Attached Campaigns Files'},
        ),
        migrations.AlterField(
            model_name='attachedfiles',
            name='campaign_file',
            field=models.FileField(blank=True, null=True, upload_to='attached_files/2018/11/24'),
        ),
        migrations.AlterField(
            model_name='usersavedcampaigns',
            name='saved_campaign',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='saved_campaign', to='Sender.Campaign'),
        ),
    ]