# Generated by Django 3.2 on 2021-05-21 13:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('newref', '0021_ref_public_key'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ref',
            name='crypted_email_host_password',
            field=models.BinaryField(blank=True, max_length=3000, null=True),
        ),
    ]
