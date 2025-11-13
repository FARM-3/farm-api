# Drying Model Design Document

## Overview
Complete redesign of the Sundrying model to track daily drying progress with automated calculations and weekly lot consolidation.

## Model Structure

### Drying Model Fields

#### User-Provided Fields
- `processing_id` (FK to Processing, nullable, blank)
  - Monday-Sunday: Can select existing processing IDs
  - Monday onwards: NULL (locked, use lot_id instead)

- `lot_id` (CharField, max_length=10, auto-generated, e.g., "W001", "W002")
  - Auto-generated as W001-W52 based on week
  - Immutable after creation

- `date` (DateField)
  - Date of drying entry

- `weather_condition` (CharField, max_length=50, blank=True)
  - User enters: cloudy, sunny, drizzle, etc.
  - No choices (frontend handles validation)

- `moisture_content` (DecimalField, max_digits=5, decimal_places=2)
  - Current day's moisture percentage (%)
  - Required daily entry

- `weight` (DecimalField, max_digits=10, decimal_places=2, nullable, blank=True)
  - Current day's weight (kg)
  - Optional, for tracking weight loss

- `weight_before` (DecimalField, max_digits=10, decimal_places=2, nullable, blank=True)
  - Previous day's weight (for rate calculation)
  - Required only on day 1; auto-filled from previous entry after

- `moisture_before` (DecimalField, max_digits=5, decimal_places=2, nullable, blank=True)
  - Previous day's moisture (for rate calculation)
  - Required only on day 1; auto-filled from previous entry after

#### Auto-Generated Fields
- `processing_type` (CharField, max_length=50)
  - Auto-filled from processing_id.processing_type
  - Null if using lot_id (Monday+ entries)

- `type_of_coffee` (CharField, max_length=50, nullable, blank=True)
  - Filled on day 1 from processing_id
  - Auto-filled on subsequent days if same processing_id
  - Null if using lot_id

- `days` (IntegerField, read-only)
  - Days since processing_id was created (or since lot start on Monday)
  - Mon-Sun: days since processing_id creation
  - Monday+: days since lot creation (or NULL if lot-based entry)

- `moisture_deviation` (DecimalField, max_digits=5, decimal_places=2, read-only)
  - Ideal moisture: 12%
  - Formula: current_moisture - 12
  - E.g., 15% → +3, 10% → -2

- `rate_of_drying` (DecimalField, max_digits=5, decimal_places=2, read-only)
  - Formula: moisture_before - moisture_content
  - Day 1: 0 (no previous moisture)
  - Mon-Sun (processing_id): previous day of same processing_id
  - Monday (lot): average of all last week's final moistures - today's moisture

- `rate_of_weightloss` (DecimalField, max_digits=10, decimal_places=2, read-only)
  - Formula: weight_before - weight
  - Day 1: 0 (no previous weight)
  - Mon-Sun: previous day of same processing_id
  - Monday: total weight of all lot entries on Sunday - today's weight

- `outturn` (DecimalField, max_digits=5, decimal_places=2, read-only)
  - Percentage weight loss from first day
  - Formula: ((first_day_weight - current_weight) / first_day_weight) * 100
  - Mon-Sun: based on first entry of this processing_id
  - Monday: based on combined first day weight of all lot processing_ids

- `outturn_deviation` (DecimalField, max_digits=5, decimal_places=2, read-only)
  - Target outturn: 60%
  - Formula: outturn - 60
  - E.g., 63% → +3, 58% → -2

#### Metadata
- `created_at` (DateTimeField, auto_now_add=True)
- `updated_at` (DateTimeField, auto_now=True)

## Business Logic Rules

### Lot ID Assignment
1. Generate lot_id as W01-W52 based on ISO week number
2. Lot spans Monday (week start) to Sunday (week end)
3. All drying entries in a calendar week share same lot_id
4. Lot ID is immutable once assigned

### Processing ID vs Lot ID Selection
**Monday-Sunday (Week Days):**
- User can select `processing_id` from existing IDs
- `lot_id` is auto-assigned (read-only)
- `processing_type` and `type_of_coffee` auto-filled from processing_id

**Monday (New Week):**
- Previous week's processing_ids are LOCKED (cannot be used)
- User can only select from:
  - Existing lot_id (continue previous week's consolidation)
  - New processing_id (new batch, new lot)
- If selecting lot_id: `processing_id` must be NULL
- If selecting processing_id: `lot_id` auto-generates for new week

### Auto-Fill Logic

**Day 1 of Processing ID:**
- `moisture_before` and `weight_before`: User can provide optional values
  - If not provided: assume same as current day's values
- `type_of_coffee`: User enters, then locked for same processing_id

**Day 2+ of Same Processing ID:**
- `moisture_before`: Auto-filled from previous day (same processing_id)
- `weight_before`: Auto-filled from previous day (same processing_id)
- `type_of_coffee`: Auto-filled from day 1 entry

**Monday (Lot Consolidation):**
- `moisture_before`: Average of all last 7 days' final moisture values (all processing_ids in lot)
- `weight_before`: Sum of all Sunday weights from previous week (all processing_ids in lot)
- `type_of_coffee`: NULL (lot is combined)
- `processing_type`: NULL (lot is combined)
- First day weight for outturn calculation: Sum of all first-day weights of processing_ids in lot

### Calculation Rules

#### rate_of_drying
```
if processing_id (any day):
    rate = moisture_before - moisture_content
    // On day 1: user enters moisture_before manually
    // On day 2+: auto-filled from previous day
elif lot_id (Monday entry):
    rate = avg(all previous moistures) - moisture_content
```

#### rate_of_weightloss
```
if processing_id (any day):
    rate = weight_before - weight
    // On day 1: user enters weight_before manually
    // On day 2+: auto-filled from previous day
elif lot_id (Monday entry):
    rate = sum(all Sunday weights) - weight
```

#### outturn
```
if processing_id (Mon-Sun):
    first_weight = weight from day 1 of this processing_id
    outturn = ((first_weight - current_weight) / first_weight) * 100
elif lot_id (Monday entry):
    first_weight = sum(all day 1 weights of processing_ids in lot)
    outturn = ((first_weight - current_weight) / first_weight) * 100
```

#### moisture_deviation
```
moisture_deviation = moisture_content - 12
```

#### outturn_deviation
```
outturn_deviation = outturn - 60
```

#### days
```
if processing_id:
    days = (current_date - processing_id.created_date).days
elif lot_id:
    days = (current_date - lot_start_date).days  // Monday of this week
```

## Validation Rules

1. **processing_id and lot_id cannot both be set**
   - One or the other, never both

2. **processing_id can only be used Mon-Sun**
   - Validation on creation: if date is Monday and processing_id from previous week, reject

3. **lot_id is auto-assigned, not user-selected (on initial entry)**
   - Except when consolidating on Monday (optional to continue existing lot)

4. **moisture_content is required**
   - Always mandatory

5. **weight is optional but recommended**

6. **moisture_before and weight_before**
   - Required on day 1 (if not provided, default to current day value)
   - Auto-filled after day 1 (user can override if needed)

## Data Flow Example

### Week 1 (Mon-Sun)
```
2025-11-17 (Mon): processing_id=P001, moisture=70%, weight=100kg, lot_id=W47
2025-11-18 (Tue): processing_id=P001, moisture=68%, weight=98kg, lot_id=W47
2025-11-19 (Wed): processing_id=P001, moisture=66%, weight=96kg, lot_id=W47
2025-11-20 (Thu): processing_id=P002, moisture=72%, weight=110kg, lot_id=W47 (new batch, same week)
...
2025-11-23 (Sun): processing_id=P002, moisture=60%, weight=88kg, lot_id=W47
```

### Week 2 (Monday - Consolidation)
```
2025-11-24 (Mon):
  - Can select: new processing_id (P003) OR continue as lot_id=W47
  - If continue lot_id=W47:
    - moisture_before = avg(P001 final, P002 final) = avg(52%, 60%) = 56%
    - weight_before = 76 + 88 = 164kg (combined Sunday weights)
    - moisture_content = 54%
    - rate_of_drying = 56% - 54% = 2%
    - outturn = ((P001_first + P002_first - current_weight) / (P001_first + P002_first)) * 100
```

## Implementation Notes

1. **No separate Lot model** - lot_id is a CharField generated from ISO week
2. **Minimal serializer changes** - only update Drying serializer, no changes to other models
3. **Calculation order** - all auto-generated fields calculated in save() method
4. **Frontend flexibility** - all char fields (weather_condition, type_of_coffee) are strings, no choices in backend
5. **Historical integrity** - never delete entries, just lock old processing_ids after week ends

## Database Migration Strategy

1. Backup existing Sundrying data (if any)
2. Delete all existing Sundrying records (complete redesign)
3. Create new Drying model with all fields
4. No foreign key changes needed to other models (processing_id FK will be added to Processing model by other team)
