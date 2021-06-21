# Generated by Django 3.2 on 2021-06-20 13:24

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('newref', '0027_auto_20210527_1037'),
    ]

    operations = [
        migrations.AddField(
            model_name='ref',
            name='csv',
            field=models.FileField(blank=True, null=True, upload_to='csv/'),
        ),
        migrations.AlterField(
            model_name='rawvote',
            name='status',
            field=models.CharField(choices=[('INIT', 'Bulletin non envoyé'), ('SENT', 'Bulletin envoyé'), ('FAIL', "Echec de l'envoi du bulletin"), ('PAP_INIT', 'Papier - Transmis'), ('PAP_OK', 'Papier - Transcrit'), ('STUCK', 'Vote arrêté')], default='INIT', max_length=10),
        ),
        migrations.AlterField(
            model_name='ref',
            name='end',
            field=models.DateField(blank=True, default=datetime.date(2021, 6, 27), null=True),
        ),
        migrations.AlterField(
            model_name='ref',
            name='start',
            field=models.DateField(blank=True, default=datetime.date(2021, 6, 20), null=True),
        ),
        migrations.AlterField(
            model_name='ref',
            name='start_time',
            field=models.TimeField(blank=True, default=datetime.datetime(2021, 6, 20, 15, 24, 33, 889984), null=True),
        ),
    ]
