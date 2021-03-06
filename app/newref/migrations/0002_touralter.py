# Generated by Django 3.2 on 2021-04-16 14:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('newref', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Touralter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('num', models.IntegerField()),
                ('results', models.JSONField()),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='newref.question')),
                ('removed_option', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='newref.option')),
            ],
        ),
    ]
