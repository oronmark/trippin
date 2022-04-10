# Generated by Django 3.2.8 on 2022-04-10 09:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trippin', '0032_alter_airportsconnection_travel_time'),
    ]

    operations = [
        migrations.RenameField(
            model_name='airportsconnection',
            old_name='travel_time',
            new_name='duration',
        ),
        migrations.AddField(
            model_name='airportsconnection',
            name='legs',
            field=models.IntegerField(default=1),
        ),
    ]
