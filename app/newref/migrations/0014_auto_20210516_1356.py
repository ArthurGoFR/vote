# Generated by Django 3.2 on 2021-05-16 11:56

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('newref', '0013_auto_20210507_2057'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ref',
            name='depouillement',
            field=models.CharField(choices=[('ALT', 'Choix : Hiérarchisation des options (par Drag & Drop) - Comptabilisation : vote alternatif'), ('CLASSIC', "Choix : Sélection d'une option - Comptabilisation : Classique"), ('JUG', 'Jugement majoritaire')], default='ALT', max_length=10),
        ),
        migrations.AlterField(
            model_name='ref',
            name='end',
            field=models.DateField(blank=True, default=datetime.date(2021, 5, 23), null=True),
        ),
        migrations.AlterField(
            model_name='ref',
            name='start',
            field=models.DateField(blank=True, default=datetime.date(2021, 5, 16), null=True),
        ),
        migrations.CreateModel(
            name='Tour',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('results', models.JSONField()),
                ('ref', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='newref.ref')),
            ],
        ),
    ]
