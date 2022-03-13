# Generated by Django 3.2.8 on 2022-03-09 08:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('trippin', '0015_auto_20220307_1505'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='flight',
            name='flight_details',
        ),
        migrations.AddField(
            model_name='flightroute',
            name='transportation',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='transportation', to='trippin.transportation'),
        ),
        migrations.AlterField(
            model_name='driveroute',
            name='transportation',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='transportation', to='trippin.transportation'),
        ),
        migrations.AlterField(
            model_name='flightroute',
            name='flight_0',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='flight_0', to='trippin.flight'),
        ),
        migrations.AlterField(
            model_name='flightroute',
            name='flight_1',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='flight_1', to='trippin.flight'),
        ),
        migrations.AlterField(
            model_name='transitroute',
            name='transportation',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='transportation', to='trippin.transportation'),
        ),
    ]
