import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('financialmanagement', '0016_customer_sale_customer'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('export_ops', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='inventorylot',
            name='qr_code',
            field=models.CharField(blank=True, help_text='Scan payload e.g. LOT:W38', max_length=255),
        ),
        migrations.AddField(
            model_name='dispatchnote',
            name='proof_notes',
            field=models.TextField(blank=True, help_text='Gate proof — signature ref, photo note, etc.'),
        ),
        migrations.AddField(
            model_name='dispatchnote',
            name='sale',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='dispatches',
                to='financialmanagement.sale',
            ),
        ),
        migrations.CreateModel(
            name='ExportComplianceDocument',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('harvest_id', models.CharField(db_index=True, max_length=100)),
                ('document_type', models.CharField(
                    choices=[
                        ('land_title', 'Land title / tenure'),
                        ('permit', 'Permit / licence'),
                        ('photo_plot', 'Plot / geolocation photo'),
                        ('contract', 'Purchase contract'),
                        ('other', 'Other'),
                    ],
                    default='other',
                    max_length=30,
                )),
                ('title', models.CharField(max_length=200)),
                ('file', models.FileField(blank=True, null=True, upload_to='export_compliance/%Y/')),
                ('notes', models.TextField(blank=True)),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('uploaded_by', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'ordering': ['-uploaded_at'],
            },
        ),
    ]
