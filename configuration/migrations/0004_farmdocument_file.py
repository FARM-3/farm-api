from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('configuration', '0003_farmdocument_trainingrecord_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='farmdocument',
            name='file',
            field=models.FileField(blank=True, null=True, upload_to='documents/%Y/%m/'),
        ),
        migrations.AlterField(
            model_name='farmdocument',
            name='file_url',
            field=models.URLField(blank=True, help_text='Legacy external URL; prefer file upload'),
        ),
    ]
