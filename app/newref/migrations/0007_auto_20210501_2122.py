# Generated by Django 3.2 on 2021-05-01 19:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('newref', '0006_auto_20210501_1107'),
    ]

    operations = [
        migrations.AddField(
            model_name='ref',
            name='bulletin_objet',
            field=models.CharField(blank=True, default='Votre bulletin de vote', max_length=300, null=True),
        ),
        migrations.AlterField(
            model_name='ref',
            name='bulletin_img',
            field=models.CharField(blank=True, default='https://www.batiactu.com/images/auto/620-465-c/20200311_170654_39186406illustration-wissanu99.jpg', max_length=300, null=True),
        ),
        migrations.AlterField(
            model_name='ref',
            name='bulletin_text',
            field=models.CharField(blank=True, default='Vous êtes invité.e à voter. Attention à ne pas partager ce bulletin : les personnes qui y accéderont pourront voter à votre place.', max_length=1000, null=True),
        ),
    ]
