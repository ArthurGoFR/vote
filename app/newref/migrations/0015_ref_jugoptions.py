# Generated by Django 3.2 on 2021-05-16 13:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('newref', '0014_auto_20210516_1356'),
    ]

    operations = [
        migrations.AddField(
            model_name='ref',
            name='jugoptions',
            field=models.JSONField(default={1: 'Excellent', 2: 'Bien', 3: 'Bof', 4: 'Nul', 5: 'Rejet'}),
        ),
    ]