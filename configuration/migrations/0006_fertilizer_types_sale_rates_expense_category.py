from django.db import migrations, models


def seed_fertilizer_types(apps, schema_editor):
    FertilizerType = apps.get_model('configuration', 'FertilizerType')
    FertilizerSubType = apps.get_model('configuration', 'FertilizerSubType')
    LookupOption = apps.get_model('configuration', 'LookupOption')

    type_map = {}
    for name in ('Organic', 'Inorganic', 'Mixed'):
        ft, _ = FertilizerType.objects.get_or_create(name=name, defaults={'sort_order': len(type_map)})
        type_map[name.lower()] = ft

    organic_products = LookupOption.objects.filter(category='fertilizer_organic', is_active=True)
    for idx, opt in enumerate(organic_products):
        FertilizerSubType.objects.get_or_create(
            fertilizer_type=type_map['organic'],
            name=opt.label or opt.value,
            defaults={'sort_order': idx},
        )

    inorganic_products = LookupOption.objects.filter(category='fertilizer_inorganic', is_active=True)
    for idx, opt in enumerate(inorganic_products):
        FertilizerSubType.objects.get_or_create(
            fertilizer_type=type_map['inorganic'],
            name=opt.label or opt.value,
            defaults={'sort_order': idx},
        )

    # Seed common expense categories if none exist
    defaults = [
        'General Supplies', 'Fuel & Transport', 'Labour', 'Equipment', 'Utilities',
        'Maintenance', 'Chemicals & Inputs', 'Training', 'Other',
    ]
    for idx, cat in enumerate(defaults):
        LookupOption.objects.get_or_create(
            category='expense_category',
            value=cat,
            defaults={'label': cat, 'sort_order': idx, 'is_active': True},
        )


class Migration(migrations.Migration):

    dependencies = [
        ('configuration', '0005_fertilizer_subcategories'),
    ]

    operations = [
        migrations.AddField(
            model_name='lookupoption',
            name='default_rate',
            field=models.DecimalField(
                blank=True, decimal_places=2, help_text='Default unit price (UGX) — used for sale items',
                max_digits=14, null=True,
            ),
        ),
        migrations.AddField(
            model_name='lookupoption',
            name='unit_label',
            field=models.CharField(
                blank=True, default='kg', help_text='Unit of measure label (kg, unit, etc.)', max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name='lookupoption',
            name='category',
            field=models.CharField(
                choices=[
                    ('coffee_type', 'Coffee Type'),
                    ('coffee_variety', 'Coffee Variety'),
                    ('fertilizer', 'Fertilizer'),
                    ('fertilizer_organic', 'Organic Fertilizer Products'),
                    ('fertilizer_inorganic', 'Inorganic Fertilizer Products'),
                    ('expense_category', 'Expense Category'),
                    ('pesticide', 'Pesticide'),
                    ('standard_practice', 'Standard Practice'),
                    ('seedling_type', 'Seedling Type'),
                    ('grade', 'Grade'),
                    ('spacing', 'Tree Spacing'),
                    ('sale_item', 'Sale Item'),
                ],
                max_length=50,
            ),
        ),
        migrations.CreateModel(
            name='FertilizerType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.CharField(blank=True, max_length=255)),
                ('is_active', models.BooleanField(default=True)),
                ('sort_order', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={'ordering': ['sort_order', 'name']},
        ),
        migrations.CreateModel(
            name='FertilizerSubType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120)),
                ('sort_order', models.PositiveIntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
                ('fertilizer_type', models.ForeignKey(
                    on_delete=models.deletion.CASCADE, related_name='sub_types', to='configuration.fertilizertype',
                )),
            ],
            options={
                'ordering': ['sort_order', 'name'],
                'unique_together': {('fertilizer_type', 'name')},
            },
        ),
        migrations.RunPython(seed_fertilizer_types, migrations.RunPython.noop),
    ]
