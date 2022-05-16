# Generated by Django 3.2.8 on 2022-05-03 16:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('trippin', '0008_interest_score'),
    ]

    operations = [
        migrations.CreateModel(
            name='Trip',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='TripSegment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contribution_by_aspect', models.FloatField(default=0)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='trip_segments', to='trippin.location')),
                ('next_segment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='next_segment', to='trippin.tripsegment')),
                ('route', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='trip_segments', to='trippin.route')),
                ('trip', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='segments', to='trippin.trip')),
            ],
        ),
    ]