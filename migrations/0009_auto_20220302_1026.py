# Generated by Django 3.2.8 on 2022-03-02 08:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('trippin', '0008_auto_20220221_1032'),
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
                ('iso_region', models.CharField(max_length=6, null=True)),
                ('iso_country', models.CharField(max_length=2, null=True)),
                ('municipality', models.CharField(max_length=255, null=True)),
                ('gps_code', models.CharField(max_length=5, null=True)),
                ('iata_code', models.CharField(max_length=3, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='location',
            name='id',
        ),
        migrations.AlterField(
            model_name='location',
            name='place_id',
            field=models.CharField(max_length=255, null=True, primary_key=True, serialize=False),
        ),
        migrations.CreateModel(
            name='AirportRoute',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, null=True)),
                ('airport_0', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='airport_0', to='trippin.airport')),
                ('airport_1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='airport_1', to='trippin.airport')),
            ],
            options={
                'unique_together': {('airport_0', 'airport_1')},
            },
        ),
    ]