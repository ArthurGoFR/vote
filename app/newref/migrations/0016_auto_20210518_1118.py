# Generated by Django 3.2 on 2021-05-18 09:18

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('newref', '0015_ref_jugoptions'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ref',
            name='depouillement',
            field=models.CharField(choices=[('CLASSIC', "Choix : Sélection d'une option - Comptabilisation : Classique"), ('ALT', '(En construction) Choix Hiérarchisation des options - Comptabilisation : vote alternatif'), ('JUG', '(En construction) Jugement majoritaire ')], default='CLASSIC', max_length=10),
        ),
        migrations.AlterField(
            model_name='ref',
            name='end',
            field=models.DateField(blank=True, default=datetime.date(2021, 5, 25), null=True),
        ),
        migrations.AlterField(
            model_name='ref',
            name='secret_key',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='ref',
            name='start',
            field=models.DateField(blank=True, default=datetime.date(2021, 5, 18), null=True),
        ),
    ]
