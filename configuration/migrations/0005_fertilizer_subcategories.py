from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('configuration', '0004_farmdocument_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lookupoption',
            name='category',
            field=models.CharField(
                max_length=50,
                choices=[
                    ('coffee_type', 'Coffee Type'),
                    ('coffee_variety', 'Coffee Variety'),
                    ('fertilizer', 'Fertilizer'),
                    ('fertilizer_organic', 'Organic Fertilizer Products'),
                    ('fertilizer_inorganic', 'Inorganic Fertilizer Products'),
                    ('pesticide', 'Pesticide'),
                    ('standard_practice', 'Standard Practice'),
                    ('seedling_type', 'Seedling Type'),
                    ('grade', 'Grade'),
                    ('spacing', 'Tree Spacing'),
                    ('sale_item', 'Sale Item'),
                ],
            ),
        ),
    ]
