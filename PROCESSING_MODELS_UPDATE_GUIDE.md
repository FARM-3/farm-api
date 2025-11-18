# Processing Models Update Guide

## Overview
The Fermenting, Washing, and Natural Sundrying models have been completely redesigned to link to Quality Control (Floating) grade_ids instead of using standalone grade fields.

**Date:** 2025-01-14
**Models Updated:** Fermenting, Washing
**Models Added:** NaturalSundrying

---

## Summary of Changes

### 1. Fermenting Model (REPLACED)

**Old Structure:**
- processing_id (manual)
- name
- grade (choices: A/B/C)
- cherry_colour
- days (manual input)
- date
- weight_before
- weight_after

**New Structure:**
- processing_id (auto-generated: FERM-{YYYYMMDD}-{SEQ})
- grade (ForeignKey to Floating.grade_id)
- start_date
- end_date
- days (auto-calculated from dates)
- weight (after fermenting)

### 2. Washing Model (REPLACED)

**Old Structure:**
- processing_id (auto-generated)
- name
- grade (choices: A/B/C)
- cherry_colour
- date
- weight_before
- weight_after

**New Structure:**
- processing_id (auto-generated: WASH-{YYYYMMDD}-{SEQ})
- grade (ForeignKey to Floating.grade_id)
- date
- weight (after washing)

### 3. NaturalSundrying Model (NEW)

**Structure:**
- processing_id (auto-generated: SUND-{YYYYMMDD}-{SEQ})
- grade (ForeignKey to Floating.grade_id)
- start_date
- weight (before sundrying)

---

## Key Architectural Changes

### Before (Old Design):
```
Harvest → Processing (Fermenting/Washing)
          ↓ (standalone grade field)
```

### After (New Design):
```
Harvest → Quality Control (Ripeness/Floating)
          ↓ (grade_id generated)
          ↓
          Processing (Fermenting/Washing/Sundrying)
          ↓ (references grade_id)
```

---

## Files Modified

| File | Status | Changes |
|------|--------|---------|
| [processing/models.py](processing/models.py) | ✅ Updated | Replaced Fermenting, Washing; Added NaturalSundrying |
| [processing/serializers.py](processing/serializers.py) | ✅ Updated | Updated serializers for all 3 models |
| [processing/views.py](processing/views.py) | ✅ Updated | Updated viewsets for all 3 models |
| [processing/urls.py](processing/urls.py) | ✅ Updated | Added sundrying endpoint |

---

## Migration Strategy

Since the models have changed significantly, you have **three options** for handling migrations:

###  Option 1: Fresh Start (Recommended for Development)

**Use if:** You have no production data or data can be deleted

```bash
# 1. Delete old migration files (keep __init__.py)
rm processing/migrations/0001_initial.py
rm processing/migrations/0002_*.py
rm processing/migrations/0003_*.py
# Keep only __init__.py

# 2. Delete database tables (in Django shell or DB admin)
python manage.py dbshell
DROP TABLE processing_fermenting CASCADE;
DROP TABLE processing_washing CASCADE;
\q

# 3. Create fresh migrations
python manage.py makemigrations processing

# 4. Apply migrations
python manage.py migrate processing
```

### Option 2: Custom Data Migration (Recommended for Production)

**Use if:** You need to preserve existing data

Steps:

#### Step 1: Create empty migrations
```bash
python manage.py makemigrations processing --empty --name backup_old_data
python manage.py makemigrations processing --empty --name drop_old_models
python manage.py makemigrations processing --empty --name create_new_models
```

#### Step 2: Edit migrations manually

**Migration 1: Backup old data**
```python
# processing/migrations/000X_backup_old_data.py
from django.db import migrations

def backup_data(apps, schema_editor):
    Fermenting = apps.get_model('processing', 'Fermenting')
    Washing = apps.get_model('processing', 'Washing')

    # Export to JSON or copy to temporary tables
    # Implementation depends on your requirements

def reverse_backup(apps, schema_editor):
    pass

class Migration(migrations.Migration):
    dependencies = [
        ('processing', '0003_ripeness_floating'),
    ]

    operations = [
        migrations.RunPython(backup_data, reverse_backup),
    ]
```

**Migration 2: Drop old models**
```python
# processing/migrations/000X_drop_old_models.py
from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('processing', '000X_backup_old_data'),
    ]

    operations = [
        migrations.DeleteModel(name='Fermenting'),
        migrations.DeleteModel(name='Washing'),
    ]
```

**Migration 3: Create new models**
```bash
# Now create migrations normally
python manage.py makemigrations processing
```

### Option 3: Parallel Migration (Production with Zero Downtime)

**Use if:** You need zero downtime and want to migrate data gradually

1. Rename old models temporarily (Fermenting → FermentingOld)
2. Create new models alongside old ones
3. Migrate data gradually
4. Switch application to use new models
5. Delete old models

---

## Breaking Changes & Impact

### ⚠️ Data Loss Warning
- Old fermenting/washing data **cannot be automatically migrated**
- Grade field changes from CharField to ForeignKey (Floating)
- Many fields removed (name, cherry_colour, weight_before, etc.)

### API Changes

**Fermenting Endpoints:**
```
OLD: POST /api/fermenting/ { "name": "Batch1", "grade": "A", ... }
NEW: POST /api/fermenting/ { "grade": "GRA1411A00", "start_date": "2025-01-14", ... }
```

**Washing Endpoints:**
```
OLD: POST /api/washing/ { "name": "Batch1", "grade": "A", ... }
NEW: POST /api/washing/ { "grade": "GRA1411A00", "date": "2025-01-14", ... }
```

**New Sundrying Endpoints:**
```
NEW: POST /api/sundrying/ { "grade": "GRA1411A00", "start_date": "2025-01-14", ... }
```

---

## Frontend Changes Required

### Workflow Change

**Old Workflow:**
```
1. Harvest
2. Select grade manually (A/B/C)
3. Enter fermenting data
4. Enter washing data
```

**New Workflow:**
```
1. Harvest
2. Quality Control:
   a. Ripeness test → generates ripeness_score
   b. Floating test → generates grade_id (GRA..., GRB...)
3. Processing (use grade_id):
   a. Fermenting (optional)
   b. Washing (optional)
   c. Natural Sundrying (optional)
4. Continue to Drying/Bagging
```

### UI Changes

**Fermenting Form:**
- Remove: name input, grade dropdown (A/B/C), cherry colour
- Add: grade_id dropdown (fetch from /api/floating/)
- Add: start_date, end_date inputs
- Auto-display: days (calculated), processing_id (generated)

**Washing Form:**
- Remove: name input, grade dropdown (A/B/C), cherry colour, weight_before
- Add: grade_id dropdown (fetch from /api/floating/)
- Keep: date, weight inputs
- Auto-display: processing_id (generated)

**Natural Sundrying Form (NEW):**
- Add: grade_id dropdown
- Add: start_date, weight inputs
- Auto-display: processing_id (generated)

---

## Testing the New Models

### 1. Create Test Data

```bash
# Create harvest (production)
curl -X POST http://localhost:8000/api/production/harvests/ \
  -H "Content-Type: application/json" \
  -d '{
    "worker_name": "John Doe",
    "block_id": "Block01",
    "weight_on_delivery": 100.00,
    "date_of_delivery": "2025-01-14",
    "amount_paid": 50000,
    "paid_by": "Manager"
  }'

# Create ripeness test
curl -X POST http://localhost:8000/api/processing/ripeness/ \
  -H "Content-Type: application/json" \
  -d '{
    "harvest": "JO1401PA0",
    "sample_size": 100,
    "no_of_redcherry": 87
  }'

# Create floating test (Grade A)
curl -X POST http://localhost:8000/api/processing/floating/ \
  -H "Content-Type: application/json" \
  -d '{
    "harvest": "JO1401PA0",
    "grade": "A",
    "weight": 45.50
  }'
# Response will include grade_id: "GRA1401A00"

# Create fermenting process
curl -X POST http://localhost:8000/api/processing/fermenting/ \
  -H "Content-Type: application/json" \
  -d '{
    "grade": "GRA1401A00",
    "start_date": "2025-01-14",
    "end_date": "2025-01-17",
    "weight": 44.20
  }'

# Create washing process
curl -X POST http://localhost:8000/api/processing/washing/ \
  -H "Content-Type: application/json" \
  -d '{
    "grade": "GRA1401A00",
    "date": "2025-01-17",
    "weight": 43.80
  }'

# Create natural sundrying process
curl -X POST http://localhost:8000/api/processing/sundrying/ \
  -H "Content-Type: application/json" \
  -d '{
    "grade": "GRA1401A00",
    "start_date": "2025-01-17",
    "weight": 43.80
  }'
```

---

## Rollback Plan

If you need to rollback:

```bash
# 1. Revert code changes
git checkout HEAD~1 processing/models.py processing/serializers.py processing/views.py

# 2. Delete new migration files
rm processing/migrations/000X_update_processing_models.py

# 3. Revert database migrations
python manage.py migrate processing 0003_ripeness_floating

# 4. Restart application
```

---

## Next Steps

1. **Choose Migration Strategy** (Option 1, 2, or 3 above)
2. **Backup Production Database** (if applicable)
3. **Run Migrations** (based on chosen strategy)
4. **Update Frontend Code** (React Native forms)
5. **Test Complete Workflow** (Harvest → QC → Processing)
6. **Deploy to Production** (following deployment guide)

---

## Production Deployment Checklist

- [ ] Backup production database
- [ ] Test migrations on staging/local copy of production DB
- [ ] Update frontend code to use new API structure
- [ ] Coordinate downtime window (if using Option 1 or 2)
- [ ] Run migrations on production
- [ ] Verify all endpoints work
- [ ] Test complete workflow end-to-end
- [ ] Monitor for errors

---

## Questions & Support

**Common Questions:**

**Q: Can I keep old fermenting/washing data?**
A: Yes, but you'll need a custom data migration (Option 2). The data structures are incompatible, so you'll need to decide how to map old data to new structure.

**Q: Do I need to delete old data?**
A: For local development, yes (Option 1). For production, use Option 2 to preserve data.

**Q: What happens to existing processing in progress?**
A: They will be deleted when you drop the old tables. Complete all in-progress processing before migrating.

**Q: Can I run old and new models side by side?**
A: Yes (Option 3), but requires renaming old models and careful migration planning.

---

**Document Version:** 1.0
**Last Updated:** 2025-01-14
**Status:** Ready for Migration ⚠️
