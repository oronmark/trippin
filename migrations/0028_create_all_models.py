# Generated by Django 3.2.8 on 2022-03-29 10:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('trippin', '0027_delete_all_models'),
    ]

    operations = [
        migrations.CreateModel(
            name='Airport',
            fields=[
                ('id', models.CharField(max_length=255, null=True, primary_key=True, serialize=False)),
                ('type', models.CharField(max_length=255, null=True)),
                ('name', models.CharField(max_length=255, null=True)),
                ('latitude_deg', models.FloatField()),
                ('longitude_deg', models.FloatField()),
                ('continent', models.CharField(max_length=2, null=True)),
                ('iso_region', models.CharField(max_length=255, null=True)),
                ('iso_country', models.CharField(max_length=2, null=True)),
                ('municipality', models.CharField(max_length=255, null=True)),
                ('gps_code', models.CharField(max_length=5, null=True)),
                ('iata_code', models.CharField(max_length=3, null=True)),
                ('connections_update_time', models.DateTimeField(default=None, null=True)),
                ('metropolitan_iata_code', models.CharField(max_length=3, null=True)),
            ],
            options={
                'unique_together': {('iata_code', 'id')},
            },
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, null=True)),
                ('place_id', models.CharField(max_length=255, null=True)),
                ('lng', models.FloatField()),
                ('lat', models.FloatField()),
                ('country', models.CharField(max_length=2)),
                ('routes_update_time', models.DateTimeField(default=None, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Route',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, null=True)),
                ('location_0', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='location_0', to='trippin.location')),
                ('location_1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='location_1', to='trippin.location')),
            ],
            options={
                'unique_together': {('location_0', 'location_1')},
            },
        ),
        migrations.CreateModel(
            name='Transportation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, null=True)),
                ('distance', models.IntegerField(null=True)),
                ('duration', models.IntegerField(null=True)),
                ('legs', models.IntegerField(null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TransitRoute',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, null=True)),
                ('route', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='route_options', to='trippin.route')),
                ('transportation', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='transportation', to='trippin.transportation')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Interest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, null=True)),
                ('aspect', models.CharField(choices=[('SKI', 'Ski'), ('HIKING', 'Hiking'), ('BEACH', 'Beach'), ('MUSEUM', 'Museum'), ('PARTY', 'Party'), ('AMUSEMENT_PARK', 'Amusement_park'), ('CITY', 'City'), ('CULINARY', 'Culinary'), ('LOCAL_CULTURE', 'Local_culture'), ('NIGHT_LIFE', 'Night_life')], max_length=255)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='interests', to='trippin.location')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='DriveRoute',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, null=True)),
                ('route', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='route_options', to='trippin.route')),
                ('transportation', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='transportation', to='trippin.transportation')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AirportLocation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, null=True)),
                ('airport', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='airport', to='trippin.airport')),
                ('airport_transportation', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='airport_transportation', to='trippin.transportation')),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='location', to='trippin.location')),
            ],
            options={
                'unique_together': {('airport', 'location')},
            },
        ),
        migrations.CreateModel(
            name='FlightRoute',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, null=True)),
                ('airport_location_0', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='airport_location_0', to='trippin.airportlocation')),
                ('airport_location_1', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='airport_location_1', to='trippin.airportlocation')),
                ('route', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='route_options', to='trippin.route')),
                ('transportation', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='transportation', to='trippin.transportation')),
            ],
            options={
                'unique_together': {('airport_location_0', 'airport_location_1')},
            },
        ),
        migrations.CreateModel(
            name='AirportsConnection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, null=True)),
                ('distance', models.IntegerField()),
                ('travel_time', models.IntegerField()),
                ('airport_0', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='airport_0', to='trippin.airport')),
                ('airport_1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='airport_1', to='trippin.airport')),
            ],
            options={
                'unique_together': {('airport_0', 'airport_1')},
            },
        ),
    ]
