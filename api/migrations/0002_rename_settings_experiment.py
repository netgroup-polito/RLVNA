# Generated by Django 4.0.4 on 2022-04-26 17:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Settings',
            new_name='Experiment',
        ),
    ]
