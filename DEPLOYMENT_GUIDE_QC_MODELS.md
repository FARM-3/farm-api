# Deployment Guide: Quality Control Models (Ripeness & Floating)

## Overview
This guide covers deploying the new Quality Control models to production (Digital Ocean) safely.

**Created:** 2025-01-14
**Commit Before Changes:** `7537bc1`
**New Models:** `Ripeness`, `Floating` (in processing app)

---

## Safety Guarantees

### ✅ What This Migration Does (Safe Operations)
- **Creates** `processing_ripeness` table (NEW)
- **Creates** `processing_floating` table (NEW)
- **Adds** foreign keys to existing `production_harvests` table
- **Creates** indexes for performance

### ✅ What This Migration Does NOT Do (No Risk)
- ❌ Does NOT modify existing tables
- ❌ Does NOT delete any data
- ❌ Does NOT change existing foreign keys
- ❌ Does NOT alter existing columns
- ❌ Does NOT require downtime

### Migration Dependencies
```
processing/migrations/0003_ripeness_floating.py
├─ Depends on: processing/0002_drying_delete_sundrying
└─ Depends on: production/0003_alter_harvests_block_id_alter_harvests_paid_by
```

**Important:** Production must have `production_harvests` table. Since you're at commit `7537bc1` which includes production app, this is ✅ satisfied.

---

## Pre-Deployment Checklist

### On Local Machine (Before Push)

- [ ] **Verify migration file exists:**
  ```bash
  ls processing/migrations/0003_ripeness_floating.py
  ```
  Expected: File should exist

- [ ] **Verify models are in code:**
  ```bash
  grep "class Ripeness" processing/models.py
  grep "class Floating" processing/models.py
  ```
  Expected: Both classes should be found

- [ ] **Check git status:**
  ```bash
  git status
  ```
  Expected files to commit:
  - `processing/models.py` (modified)
  - `processing/migrations/0003_ripeness_floating.py` (new)
  - `QUALITY_CONTROL_FRONTEND_GUIDE.md` (new)

- [ ] **Commit changes:**
  ```bash
  git add processing/models.py
  git add processing/migrations/0003_ripeness_floating.py
  git add QUALITY_CONTROL_FRONTEND_GUIDE.md
  git commit -m "Add Quality Control models (Ripeness and Floating) for processing"
  ```

- [ ] **Push to repository:**
  ```bash
  git push origin main
  ```

---

## Production Deployment Steps (Digital Ocean)

### Step 1: Backup Database (Recommended)
```bash
# SSH into Digital Ocean droplet
ssh your-user@your-server

# Navigate to project directory
cd /path/to/your/api

# Create database backup
pg_dump your_db_name > backup_before_qc_models_$(date +%Y%m%d_%H%M%S).sql

# Or if using managed database:
# Use Digital Ocean console to create snapshot
```

### Step 2: Pull New Code
```bash
# Pull latest changes
git pull origin main

# Verify new files are present
ls processing/migrations/0003_ripeness_floating.py
```

### Step 3: Activate Virtual Environment
```bash
# Activate venv (adjust path as needed)
source venv/bin/activate

# Or if using different venv name:
# source env/bin/activate
```

### Step 4: Check Migration Status
```bash
# Check what migrations will be applied
python manage.py showmigrations processing

# Expected output:
# processing
#  [X] 0001_initial
#  [X] 0002_drying_delete_sundrying
#  [ ] 0003_ripeness_floating  <- This should be unchecked
```

### Step 5: Apply Migrations
```bash
# Run migrations for processing app
python manage.py migrate processing

# Expected output:
# Operations to perform:
#   Apply all migrations: processing
# Running migrations:
#   Applying processing.0003_ripeness_floating... OK
```

### Step 6: Verify Tables Created
```bash
# Check that new tables exist
python manage.py dbshell

# In PostgreSQL shell, run:
\dt processing_*

# Expected output should include:
#  processing_ripeness
#  processing_floating

# Exit shell
\q
```

### Step 7: Restart Application (if needed)
```bash
# If using Gunicorn with systemd:
sudo systemctl restart gunicorn

# If using Gunicorn directly:
pkill gunicorn && gunicorn api.wsgi:application

# If using other WSGI server, restart accordingly
```

### Step 8: Verify API Endpoints (After Backend Setup)
```bash
# Test that models are accessible (once serializers/views are added)
curl http://your-domain.com/api/ripeness/
curl http://your-domain.com/api/floating/

# For now, these will 404 until you add views/URLs
```

---

## Rollback Plan (If Needed)

### If Something Goes Wrong

**Option 1: Undo Migration**
```bash
# Reverse the migration
python manage.py migrate processing 0002_drying_delete_sundrying

# This will DROP the new tables
# No data loss (since tables are new and empty)
```

**Option 2: Restore from Backup**
```bash
# Restore database from backup
psql your_db_name < backup_before_qc_models_YYYYMMDD_HHMMSS.sql
```

**Option 3: Revert Code**
```bash
# Go back to previous commit
git revert HEAD
git push origin main

# Then on server:
git pull origin main
python manage.py migrate processing 0002
```

---

## Post-Deployment Verification

### Verify Migration Applied
```bash
python manage.py showmigrations processing

# All should be checked:
# processing
#  [X] 0001_initial
#  [X] 0002_drying_delete_sundrying
#  [X] 0003_ripeness_floating  <- Should now be checked
```

### Verify Tables Exist
```sql
-- Connect to database
python manage.py dbshell

-- Check processing_ripeness table
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'processing_ripeness';

-- Check processing_floating table
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'processing_floating';

-- Both should return table structure
```

### Verify Foreign Keys
```sql
-- Check foreign key from ripeness to harvests
SELECT
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
  ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
  ON ccu.constraint_name = tc.constraint_name
WHERE tc.table_name = 'processing_ripeness';

-- Should show: harvest_id -> production_harvests
```

---

## Expected Database Schema After Migration

### processing_ripeness
| Column | Type | Constraints |
|--------|------|-------------|
| harvest_id | VARCHAR(20) | PRIMARY KEY, FK to production_harvests |
| date | DATE | NOT NULL, default: CURRENT_DATE |
| sample_size | INTEGER | NOT NULL, default: 100, CHECK >= 1 |
| no_of_redcherry | INTEGER | NOT NULL, CHECK >= 0 |
| ripeness_score | NUMERIC(5,2) | NOT NULL, CHECK 0-100 |
| created_at | TIMESTAMP | NOT NULL |
| updated_at | TIMESTAMP | NOT NULL |

### processing_floating
| Column | Type | Constraints |
|--------|------|-------------|
| grade_id | VARCHAR(20) | PRIMARY KEY, UNIQUE |
| harvest_id | VARCHAR(20) | FK to production_harvests |
| grade | VARCHAR(50) | NOT NULL |
| weight | NUMERIC(10,2) | NOT NULL, CHECK >= 0 |
| date | DATE | NOT NULL, default: CURRENT_DATE |
| ripeness_score | NUMERIC(5,2) | NULL, CHECK 0-100 |
| created_at | TIMESTAMP | NOT NULL |
| updated_at | TIMESTAMP | NOT NULL |

---

## Troubleshooting

### Issue: "relation production_harvests does not exist"
**Cause:** Production app not migrated
**Solution:**
```bash
python manage.py migrate production
```

### Issue: "column harvest_id violates foreign key constraint"
**Cause:** Trying to create Ripeness/Floating for non-existent harvest
**Solution:** Ensure harvest exists in production_harvests before creating QC records

### Issue: Migration shows as applied but tables don't exist
**Cause:** Migration was faked or database out of sync
**Solution:**
```bash
# Check actual tables
python manage.py dbshell
\dt processing_*

# If missing, manually run migration SQL:
python manage.py sqlmigrate processing 0003 | python manage.py dbshell
```

---

## Next Steps After Deployment

1. **Create Serializers** (for REST API):
   - `processing/serializers.py`: RipenessSerializer, FloatingSerializer

2. **Create ViewSets** (for API endpoints):
   - `processing/views.py`: RipenessViewSet, FloatingViewSet

3. **Register URLs**:
   - `processing/urls.py`: Add routes for ripeness and floating

4. **Test API Endpoints**:
   - POST /api/ripeness/
   - GET /api/ripeness/
   - POST /api/floating/
   - GET /api/floating/

5. **Update Frontend** (React Native):
   - Refer to [QUALITY_CONTROL_FRONTEND_GUIDE.md](QUALITY_CONTROL_FRONTEND_GUIDE.md)

---

## Important Notes

### Migration Compatibility
- This migration is **forward-compatible** only
- Once applied, database has new tables
- Code without these models will still work (tables just unused)
- Code with these models requires migration applied

### Zero Downtime Deployment
This migration supports zero-downtime deployment:
1. New tables are created (doesn't affect existing code)
2. Old code continues working (doesn't use new tables)
3. Deploy new code (starts using new tables)
4. No interruption to users

### Production Database State
At commit `7537bc1`, your production should have:
- ✓ production_harvests table
- ✓ production_block table
- ✓ processing_fermenting table
- ✓ processing_washing table
- ✓ processing_drying table
- ✓ processing_bagging table

After this migration:
- ✓ All above (unchanged)
- ✓ processing_ripeness (new)
- ✓ processing_floating (new)

---

## Contact & Support

If you encounter issues during deployment:
1. Check error logs: `tail -f /var/log/your-app/error.log`
2. Check Django logs: `python manage.py runserver` output
3. Verify PostgreSQL logs: `sudo tail -f /var/log/postgresql/postgresql-*.log`

**Rollback is always safe** - just reverse the migration or restore backup.

---

**Document Version:** 1.0
**Last Updated:** 2025-01-14
**Status:** Ready for Deployment ✅
