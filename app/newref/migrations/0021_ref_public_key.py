# Generated by Django 3.2 on 2021-05-21 12:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('newref', '0020_alter_ref_crypted'),
    ]

    operations = [
        migrations.AddField(
            model_name='ref',
            name='public_key',
            field=models.FileField(blank=True, null=True, upload_to='public_keys/'),
        ),
    ]
