# Generated by Django 3.2.8 on 2022-04-06 15:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trippin', '0030_create_all_models'),
    ]

    operations = [
        migrations.RenameField(
            model_name='airport',
            old_name='latitude_deg',
            new_name='lat',
        ),
        migrations.RenameField(
            model_name='airport',
            old_name='longitude_deg',
            new_name='lng',
        ),
    ]
