# Quality Control Models - Frontend Implementation Guide

## Overview
This document provides comprehensive guidance for implementing the Quality Control features in React Native. The backend handles data validation and calculations, while the frontend manages user interface, choices, and data submission.

**Created:** 2025-01-14
**Backend Models:** `Ripeness`, `Floating` (in `processing` app)
**Related Model:** `Harvests` (in `production` app)

---

## Table of Contents
1. [Model Architecture](#model-architecture)
2. [Ripeness Test Implementation](#ripeness-test-implementation)
3. [Floating Test Implementation](#floating-test-implementation)
4. [API Endpoints](#api-endpoints)
5. [Frontend Responsibilities](#frontend-responsibilities)
6. [Validation Rules](#validation-rules)
7. [User Flow](#user-flow)

---

## Model Architecture

### Database Relationships
```
production.Harvests (1) ←→ (1) processing.Ripeness
production.Harvests (1) ←→ (many) processing.Floating
```

- **Each harvest has ONE ripeness test**
- **Each harvest can have MULTIPLE floating tests** (typically one for Grade A, one for Grade B)

---

## Ripeness Test Implementation

### Backend Model: `Ripeness`
**Location:** `processing/models.py`

### Fields Overview
| Field | Type | Backend Logic | Frontend Responsibility |
|-------|------|---------------|------------------------|
| `harvest` | ForeignKey | OneToOne relationship | Harvest selection dropdown |
| `date` | DateField | Default: today | Date picker (pre-filled with today) |
| `sample_size` | PositiveIntegerField | Default: 100 | Editable input (pre-filled with 100) |
| `no_of_redcherry` | PositiveIntegerField | Stored as-is | User input (0 to sample_size) |
| `ripeness_score` | DecimalField | **AUTO-CALCULATED** | Display only (read-only) |
| `created_at` | DateTimeField | Auto-generated | Display only |
| `updated_at` | DateTimeField | Auto-generated | Display only |

### Auto-Calculated Fields
- **`ripeness_score`**: Calculated as `(no_of_redcherry / sample_size) * 100`
  - Backend calculates this automatically in the `save()` method
  - Frontend should display this after submission (read-only)

### Frontend Implementation Tasks

#### 1. Harvest Selection
```javascript
// Example API call to get available harvests
GET /api/harvests/

// Filter: Only show harvests that DON'T have a ripeness test yet
// Backend query: Harvests.objects.filter(ripeness_test__isnull=True)
```

**UI Component:**
- Dropdown/Select component
- Display: `{harvest_id} - {worker_name}`
- Show only harvests without existing ripeness tests

#### 2. Date Input
**UI Component:**
- Date picker
- Pre-fill with current date
- Allow user to change if needed

#### 3. Sample Size Input
**UI Component:**
- Number input field
- Pre-fill with `100`
- Editable
- Validation: Must be ≥ 1

#### 4. Red Cherry Count Input
**UI Component:**
- Number input field
- Validation: Must be ≥ 0 and ≤ sample_size
- Show real-time error if exceeds sample_size

#### 5. Ripeness Score Display
**After Submission:**
- Display calculated percentage (e.g., "Ripeness Score: 87.50%")
- Use color coding:
  - Green: ≥ 80%
  - Yellow: 60-79%
  - Red: < 60%

### Sample React Native Form
```jsx
const RipenessTestForm = () => {
  const [harvest, setHarvest] = useState(null);
  const [date, setDate] = useState(new Date());
  const [sampleSize, setSampleSize] = useState(100);
  const [redCherries, setRedCherries] = useState(0);

  const handleSubmit = async () => {
    const data = {
      harvest: harvest.harvest_id,
      date: date.toISOString().split('T')[0], // Format: YYYY-MM-DD
      sample_size: sampleSize,
      no_of_redcherry: redCherries
    };

    const response = await fetch('/api/ripeness/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });

    const result = await response.json();
    // Display result.ripeness_score to user
  };
};
```

---

## Floating Test Implementation

### Backend Model: `Floating`
**Location:** `processing/models.py`

### Fields Overview
| Field | Type | Backend Logic | Frontend Responsibility |
|-------|------|---------------|------------------------|
| `grade_id` | CharField | **AUTO-GENERATED** | Display only (after save) |
| `harvest` | ForeignKey | Relationship | Harvest selection dropdown |
| `grade` | CharField | Stored as-is | Grade selection (A or B) |
| `weight` | DecimalField | Stored as-is | Weight input |
| `date` | DateField | Default: today | Date picker (pre-filled) |
| `ripeness_score` | DecimalField | **AUTO-FILLED** | Display only (auto-populated) |
| `created_at` | DateTimeField | Auto-generated | Display only |
| `updated_at` | DateTimeField | Auto-generated | Display only |

### Auto-Generated Fields

#### 1. `grade_id` Format
**Format:** `GR{A/B}{DDMM}{Letter}{00-99}`

**Examples:**
- `GRA1411A00` → Grade A, November 14, first entry (A00)
- `GRB1010B22` → Grade B, October 10, entry B22 (1322nd entry)

**Logic:**
- `GR`: Prefix
- `{A/B}`: First letter of grade (uppercase)
- `{DDMM}`: Day and month (e.g., 1411 for Nov 14)
- `{Letter}`: Sequential letter A-Z (26 letters)
- `{00-99}`: Sequential number (100 numbers)
- **Total capacity:** 2,600 entries per grade per day

**Backend handles generation automatically.**

#### 2. `ripeness_score` Auto-Fill
- When creating a Floating entry, backend automatically fetches the ripeness_score from the related Ripeness test
- Frontend should display this after submission

### Frontend Implementation Tasks

#### 1. Harvest Selection
```javascript
// Option 1: Show only harvests WITH ripeness tests
GET /api/harvests/?has_ripeness=true

// Option 2: Show all harvests and display ripeness_score if available
GET /api/ripeness/?harvest={harvest_id}
```

**UI Component:**
- Dropdown/Select component
- Display: `{harvest_id} - {worker_name} (Ripeness: {score}%)`
- Show ripeness score next to harvest name for context

**Auto-Population Logic:**
```javascript
const onHarvestSelect = async (harvestId) => {
  // Fetch ripeness test for this harvest
  const response = await fetch(`/api/ripeness/?harvest=${harvestId}`);
  const ripenessData = await response.json();

  if (ripenessData.results.length > 0) {
    // Display ripeness score to user
    setRipenessScore(ripenessData.results[0].ripeness_score);
  }
};
```

#### 2. Grade Selection
**UI Component:**
- Radio buttons or segmented control
- Options:
  - **Grade A**: "Netweight (Sinkers)"
  - **Grade B**: "Floaters"

**No backend choices** - you control the options displayed.

#### 3. Weight Input
**UI Component:**
- Decimal number input
- Unit: kg
- Validation: Must be > 0
- Allow 2 decimal places

#### 4. Date Input
**UI Component:**
- Date picker
- Pre-fill with current date

#### 5. Display Auto-Generated Data
**After Submission:**
- Display `grade_id` (e.g., "Grade ID: GRA1411A00")
- Display `ripeness_score` (auto-filled from Ripeness test)

### Sample React Native Form
```jsx
const FloatingTestForm = () => {
  const [harvest, setHarvest] = useState(null);
  const [grade, setGrade] = useState('A');
  const [weight, setWeight] = useState(0);
  const [date, setDate] = useState(new Date());
  const [ripenessScore, setRipenessScore] = useState(null);

  const onHarvestSelect = async (selectedHarvest) => {
    setHarvest(selectedHarvest);

    // Auto-fetch ripeness score for display
    const response = await fetch(`/api/ripeness/?harvest=${selectedHarvest.harvest_id}`);
    const data = await response.json();
    if (data.results.length > 0) {
      setRipenessScore(data.results[0].ripeness_score);
    }
  };

  const handleSubmit = async () => {
    const data = {
      harvest: harvest.harvest_id,
      grade: grade, // Send "A" or "B"
      weight: weight,
      date: date.toISOString().split('T')[0]
    };

    const response = await fetch('/api/floating/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });

    const result = await response.json();
    // Display result.grade_id and result.ripeness_score to user
  };
};
```

---

## API Endpoints

### Ripeness Endpoints
```
GET    /api/ripeness/              # List all ripeness tests
POST   /api/ripeness/              # Create new ripeness test
GET    /api/ripeness/{harvest_id}/ # Get specific ripeness test
PUT    /api/ripeness/{harvest_id}/ # Update ripeness test
DELETE /api/ripeness/{harvest_id}/ # Delete ripeness test
```

### Floating Endpoints
```
GET    /api/floating/              # List all floating tests
POST   /api/floating/              # Create new floating test
GET    /api/floating/{grade_id}/   # Get specific floating test
PUT    /api/floating/{grade_id}/   # Update floating test
DELETE /api/floating/{grade_id}/   # Delete floating test
```

### Filter Examples
```
GET /api/ripeness/?harvest={harvest_id}
GET /api/floating/?harvest={harvest_id}
GET /api/floating/?grade=A
GET /api/floating/?date=2025-01-14
```

---

## Frontend Responsibilities

### 1. Choices & Dropdowns
- **Grade selection** (A/B) - no backend choices, frontend controls options
- **Harvest selection** - fetch from API, filter as needed
- All dropdown/choice logic is frontend-controlled

### 2. Form Validation
- Sample size ≥ 1
- Red cherries ≤ sample_size
- Weight > 0
- Date format validation
- Required field checks

### 3. User Experience
- Pre-fill default values:
  - Sample size: 100
  - Date: Current date
- Show loading states during API calls
- Display success/error messages
- Clear form after successful submission

### 4. Data Display
- Format decimal numbers (2 decimal places)
- Display percentages with % symbol
- Use color coding for ripeness scores
- Show auto-generated IDs prominently

### 5. Error Handling
```javascript
try {
  const response = await fetch('/api/ripeness/', { /*...*/ });
  if (!response.ok) {
    const error = await response.json();
    // Display error.detail or field-specific errors
    showError(error);
  }
} catch (err) {
  showError('Network error. Please try again.');
}
```

---

## Validation Rules

### Ripeness Model
| Field | Validation Rules |
|-------|------------------|
| `harvest` | Required, must exist, must not have existing ripeness test |
| `date` | Required, valid date format (YYYY-MM-DD) |
| `sample_size` | Required, integer ≥ 1 |
| `no_of_redcherry` | Required, integer ≥ 0, ≤ sample_size |

### Floating Model
| Field | Validation Rules |
|-------|------------------|
| `harvest` | Required, must exist |
| `grade` | Required, non-empty string |
| `weight` | Required, decimal > 0, max 2 decimal places |
| `date` | Required, valid date format (YYYY-MM-DD) |

---

## User Flow

### Workflow 1: Complete Quality Control Process

```
1. Harvest arrives → Recorded in production.Harvests
2. Quality Control starts:

   Step 1: Ripeness Test
   ├─ Select harvest from dropdown
   ├─ Confirm sample size (default: 100)
   ├─ Count red cherries
   ├─ Submit form
   └─ Backend calculates ripeness_score automatically

   Step 2: Floating Test (Grade A)
   ├─ Select same harvest
   ├─ Choose Grade: A (Netweight)
   ├─ Enter weight of sinkers
   ├─ Submit form
   └─ Backend generates grade_id (GRA...) and fills ripeness_score

   Step 3: Floating Test (Grade B)
   ├─ Select same harvest again
   ├─ Choose Grade: B (Floaters)
   ├─ Enter weight of floaters
   ├─ Submit form
   └─ Backend generates grade_id (GRB...) and fills ripeness_score

3. Quality Control complete → Proceed to next stage (Fermenting, etc.)
```

### Workflow 2: View Quality Control Results

```javascript
// Get all QC data for a specific harvest
const getQCData = async (harvestId) => {
  const ripeness = await fetch(`/api/ripeness/?harvest=${harvestId}`);
  const floating = await fetch(`/api/floating/?harvest=${harvestId}`);

  return {
    ripeness: await ripeness.json(),
    floating: await floating.json()
  };
};
```

---

## Best Practices

### 1. Keep Backend Flexible
- Don't add choices on backend
- Keep fields as CharFields where possible
- Let frontend control dropdown options

### 2. Reduce Backend Requests
- Cache harvest list
- Store ripeness_score locally after fetching
- Batch API calls when possible

### 3. User Feedback
- Show real-time calculations (e.g., ripeness % preview)
- Display auto-generated IDs immediately after save
- Provide clear success messages

### 4. Data Consistency
- Ensure ripeness test is created BEFORE floating tests
- Validate harvest selection across both forms
- Show warnings if data seems inconsistent

---

## Quick Reference: What Backend Does vs Frontend Does

| Task | Backend | Frontend |
|------|---------|----------|
| Calculate ripeness_score | ✅ Auto-calculate | ❌ Display only |
| Generate grade_id | ✅ Auto-generate | ❌ Display only |
| Auto-fill ripeness_score in Floating | ✅ Auto-fill | ❌ Display only |
| Validate no_of_redcherry ≤ sample_size | ✅ Validate | ✅ Real-time validation |
| Provide grade choices (A/B) | ❌ No choices | ✅ Control options |
| Harvest selection dropdown | ❌ Provide data | ✅ Display & filter |
| Date picker UI | ❌ Store date | ✅ Date picker component |
| Weight input UI | ❌ Store weight | ✅ Input component |
| Sample size default (100) | ✅ Default value | ✅ Pre-fill in form |

---

## Appendix: Sample API Payloads

### Create Ripeness Test
```json
POST /api/ripeness/

{
  "harvest": "ED0711PA1",
  "date": "2025-01-14",
  "sample_size": 100,
  "no_of_redcherry": 87
}

Response:
{
  "harvest": "ED0711PA1",
  "date": "2025-01-14",
  "sample_size": 100,
  "no_of_redcherry": 87,
  "ripeness_score": "87.00",
  "created_at": "2025-01-14T10:30:00Z",
  "updated_at": "2025-01-14T10:30:00Z"
}
```

### Create Floating Test
```json
POST /api/floating/

{
  "harvest": "ED0711PA1",
  "grade": "A",
  "weight": "45.50",
  "date": "2025-01-14"
}

Response:
{
  "grade_id": "GRA1401A00",
  "harvest": "ED0711PA1",
  "grade": "A",
  "weight": "45.50",
  "date": "2025-01-14",
  "ripeness_score": "87.00",
  "created_at": "2025-01-14T10:35:00Z",
  "updated_at": "2025-01-14T10:35:00Z"
}
```

---

## Questions or Issues?
Contact the backend team or refer to the model source code:
- **File:** `c:\Users\THINKPAD\OneDrive\Desktop\api\processing\models.py`
- **Lines:** 26-225 (Ripeness and Floating models)

---

**Document Version:** 1.0
**Last Updated:** 2025-01-14
