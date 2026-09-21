import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BlockActivityLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('log_id', models.CharField(max_length=30, unique=True)),
                ('block_id', models.CharField(db_index=True, max_length=50)),
                ('log_type', models.CharField(choices=[('practice', 'Farm Practice'), ('input', 'Input Application'), ('scouting', 'Scouting'), ('maintenance', 'Maintenance'), ('other', 'Other')], default='practice', max_length=20)),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('practices', models.JSONField(blank=True, default=list, help_text='Standard practices applied')),
                ('input_type', models.CharField(blank=True, choices=[('fertilizer', 'Fertilizer'), ('pesticide', 'Pesticide'), ('organic', 'Organic Input'), ('other', 'Other')], max_length=20)),
                ('input_name', models.CharField(blank=True, max_length=200)),
                ('quantity', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('unit', models.CharField(blank=True, help_text='kg, L, bags, etc.', max_length=30)),
                ('activity_date', models.DateField()),
                ('weather_conditions', models.JSONField(blank=True, default=list)),
                ('gps_coordinates', models.CharField(blank=True, max_length=100)),
                ('photo', models.ImageField(blank=True, null=True, upload_to='field_ops/activities/%Y/%m/')),
                ('reported_by_name', models.CharField(blank=True, max_length=200)),
                ('harvest_id', models.CharField(blank=True, help_text='Optional link to harvest lot', max_length=100)),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('reported_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='block_activity_logs', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Block Activity Log',
                'verbose_name_plural': 'Block Activity Logs',
                'ordering': ['-activity_date', '-created_at'],
            },
        ),
        migrations.CreateModel(
            name='SurveillanceReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('report_id', models.CharField(max_length=30, unique=True)),
                ('block_id', models.CharField(blank=True, db_index=True, max_length=50)),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('severity', models.CharField(choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')], default='medium', max_length=20)),
                ('issue_type', models.CharField(choices=[('pest', 'Pest Infestation'), ('disease', 'Disease'), ('drought', 'Drought / Water Stress'), ('theft', 'Theft / Damage'), ('compliance', 'Compliance Issue'), ('quality', 'Cherry Quality'), ('other', 'Other')], default='other', max_length=20)),
                ('weather_conditions', models.JSONField(blank=True, default=list)),
                ('location', models.CharField(blank=True, max_length=200)),
                ('gps_coordinates', models.CharField(blank=True, max_length=100)),
                ('photo', models.ImageField(blank=True, null=True, upload_to='field_ops/surveillance/%Y/%m/')),
                ('reported_by_name', models.CharField(blank=True, max_length=200)),
                ('status', models.CharField(choices=[('open', 'Open'), ('in_review', 'In Review'), ('resolved', 'Resolved')], default='open', max_length=20)),
                ('resolution_notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('reported_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='surveillance_reports', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Surveillance Report',
                'verbose_name_plural': 'Surveillance Reports',
                'ordering': ['-created_at'],
            },
        ),
    ]
