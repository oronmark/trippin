# Generated by Django 3.2.8 on 2022-02-20 09:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trippin', '0004_auto_20220213_1318'),
    ]

    operations = [
        migrations.RenameField(
            model_name='route',
            old_name='bus',
            new_name='driving',
        ),
        migrations.RenameField(
            model_name='route',
            old_name='car',
            new_name='flight',
        ),
        migrations.RenameField(
            model_name='route',
            old_name='train',
            new_name='transit',
        ),
        migrations.RenameField(
            model_name='route',
            old_name='walk',
            new_name='walking',
        ),
    ]