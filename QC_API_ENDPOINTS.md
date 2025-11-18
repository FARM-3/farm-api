# Quality Control API Endpoints

## Overview
Complete API documentation for the Ripeness and Floating Quality Control endpoints.

**Base URL:** `/api/processing/`

---

## Authentication
All endpoints require authentication (if enabled in your project settings).

---

## Ripeness Endpoints

### 1. List All Ripeness Tests
```http
GET /api/processing/ripeness/
```

**Response:**
```json
[
  {
    "harvest": "ED0711PA1",
    "harvest_id": "ED0711PA1",
    "date": "2025-01-14",
    "sample_size": 100,
    "no_of_redcherry": 87,
    "ripeness_score": "87.00",
    "created_at": "2025-01-14T10:30:00Z",
    "updated_at": "2025-01-14T10:30:00Z"
  }
]
```

### 2. Create Ripeness Test
```http
POST /api/processing/ripeness/
Content-Type: application/json

{
  "harvest": "ED0711PA1",
  "date": "2025-01-14",
  "sample_size": 100,
  "no_of_redcherry": 87
}
```

**Notes:**
- `ripeness_score` is auto-calculated (don't include it)
- `sample_size` defaults to 100 if not provided
- `date` defaults to today if not provided

**Response:**
```json
{
  "harvest": "ED0711PA1",
  "harvest_id": "ED0711PA1",
  "date": "2025-01-14",
  "sample_size": 100,
  "no_of_redcherry": 87,
  "ripeness_score": "87.00",
  "created_at": "2025-01-14T10:30:00Z",
  "updated_at": "2025-01-14T10:30:00Z"
}
```

### 3. Get Single Ripeness Test
```http
GET /api/processing/ripeness/{harvest_id}/
```

**Example:**
```http
GET /api/processing/ripeness/ED0711PA1/
```

### 4. Update Ripeness Test
```http
PUT /api/processing/ripeness/{harvest_id}/
Content-Type: application/json

{
  "harvest": "ED0711PA1",
  "date": "2025-01-14",
  "sample_size": 100,
  "no_of_redcherry": 90
}
```

**Or partial update:**
```http
PATCH /api/processing/ripeness/{harvest_id}/
Content-Type: application/json

{
  "no_of_redcherry": 90
}
```

### 5. Delete Ripeness Test
```http
DELETE /api/processing/ripeness/{harvest_id}/
```

### 6. Ripeness Summary Statistics
```http
GET /api/processing/ripeness/summary/
```

**Response:**
```json
{
  "total_tests": 25,
  "average_ripeness_score": 85.32,
  "passing_tests": 20,
  "failing_tests": 5,
  "pass_rate": "80.00%"
}
```

### 7. Filter Ripeness Tests
```http
# Filter by date
GET /api/processing/ripeness/?date=2025-01-14

# Filter by harvest
GET /api/processing/ripeness/?harvest=ED0711PA1

# Search by harvest ID or worker name
GET /api/processing/ripeness/?search=ED0711

# Order by ripeness score (descending)
GET /api/processing/ripeness/?ordering=-ripeness_score

# Order by date (ascending)
GET /api/processing/ripeness/?ordering=date
```

---

## Floating Endpoints

### 1. List All Floating Tests
```http
GET /api/processing/floating/
```

**Response:**
```json
[
  {
    "grade_id": "GRA1401A00",
    "harvest": "ED0711PA1",
    "harvest_id": "ED0711PA1",
    "grade": "A",
    "weight": "45.50",
    "date": "2025-01-14",
    "ripeness_score": "87.00",
    "created_at": "2025-01-14T10:35:00Z",
    "updated_at": "2025-01-14T10:35:00Z"
  }
]
```

### 2. Create Floating Test
```http
POST /api/processing/floating/
Content-Type: application/json

{
  "harvest": "ED0711PA1",
  "grade": "A",
  "weight": 45.50,
  "date": "2025-01-14"
}
```

**Notes:**
- `grade_id` is auto-generated (don't include it)
- `ripeness_score` is auto-filled from Ripeness test (don't include it)
- `date` defaults to today if not provided

**Response:**
```json
{
  "grade_id": "GRA1401A00",
  "harvest": "ED0711PA1",
  "harvest_id": "ED0711PA1",
  "grade": "A",
  "weight": "45.50",
  "date": "2025-01-14",
  "ripeness_score": "87.00",
  "created_at": "2025-01-14T10:35:00Z",
  "updated_at": "2025-01-14T10:35:00Z"
}
```

### 3. Get Single Floating Test
```http
GET /api/processing/floating/{grade_id}/
```

**Example:**
```http
GET /api/processing/floating/GRA1401A00/
```

### 4. Update Floating Test
```http
PUT /api/processing/floating/{grade_id}/
Content-Type: application/json

{
  "harvest": "ED0711PA1",
  "grade": "A",
  "weight": 46.00,
  "date": "2025-01-14"
}
```

**Or partial update:**
```http
PATCH /api/processing/floating/{grade_id}/
Content-Type: application/json

{
  "weight": 46.00
}
```

### 5. Delete Floating Test
```http
DELETE /api/processing/floating/{grade_id}/
```

### 6. Floating Summary Statistics
```http
GET /api/processing/floating/summary/
```

**Response:**
```json
{
  "overall": {
    "total_tests": 50,
    "total_weight": 2345.67
  },
  "by_grade": [
    {
      "grade": "A",
      "count": 30,
      "total_weight": 1456.50,
      "avg_weight": 48.55
    },
    {
      "grade": "B",
      "count": 20,
      "total_weight": 889.17,
      "avg_weight": 44.46
    }
  ]
}
```

### 7. Get Floating Tests by Harvest
```http
GET /api/processing/floating/by-harvest/{harvest_id}/
```

**Example:**
```http
GET /api/processing/floating/by-harvest/ED0711PA1/
```

**Response:**
```json
{
  "harvest_id": "ED0711PA1",
  "tests": [
    {
      "grade_id": "GRA1401A00",
      "harvest": "ED0711PA1",
      "harvest_id": "ED0711PA1",
      "grade": "A",
      "weight": "45.50",
      "date": "2025-01-14",
      "ripeness_score": "87.00",
      "created_at": "2025-01-14T10:35:00Z",
      "updated_at": "2025-01-14T10:35:00Z"
    },
    {
      "grade_id": "GRB1401A00",
      "harvest": "ED0711PA1",
      "harvest_id": "ED0711PA1",
      "grade": "B",
      "weight": "12.30",
      "date": "2025-01-14",
      "ripeness_score": "87.00",
      "created_at": "2025-01-14T10:36:00Z",
      "updated_at": "2025-01-14T10:36:00Z"
    }
  ],
  "total_weight": 57.80,
  "test_count": 2
}
```

### 8. Filter Floating Tests
```http
# Filter by grade
GET /api/processing/floating/?grade=A

# Filter by date
GET /api/processing/floating/?date=2025-01-14

# Filter by harvest
GET /api/processing/floating/?harvest=ED0711PA1

# Search by grade_id, grade, harvest_id, or worker name
GET /api/processing/floating/?search=GRA1401

# Order by weight (descending)
GET /api/processing/floating/?ordering=-weight

# Order by date (ascending)
GET /api/processing/floating/?ordering=date

# Combine filters
GET /api/processing/floating/?grade=A&date=2025-01-14&ordering=-weight
```

---

## Complete Workflow Example

### Step 1: Create Harvest (Production App)
This should already exist from production harvesting.

### Step 2: Create Ripeness Test
```bash
curl -X POST http://localhost:8000/api/processing/ripeness/ \
  -H "Content-Type: application/json" \
  -d '{
    "harvest": "ED0711PA1",
    "sample_size": 100,
    "no_of_redcherry": 87
  }'
```

**Response:**
```json
{
  "harvest": "ED0711PA1",
  "harvest_id": "ED0711PA1",
  "date": "2025-01-14",
  "sample_size": 100,
  "no_of_redcherry": 87,
  "ripeness_score": "87.00",
  "created_at": "2025-01-14T10:30:00Z",
  "updated_at": "2025-01-14T10:30:00Z"
}
```

### Step 3: Create Floating Test (Grade A)
```bash
curl -X POST http://localhost:8000/api/processing/floating/ \
  -H "Content-Type: application/json" \
  -d '{
    "harvest": "ED0711PA1",
    "grade": "A",
    "weight": 45.50
  }'
```

**Response:**
```json
{
  "grade_id": "GRA1401A00",
  "harvest": "ED0711PA1",
  "harvest_id": "ED0711PA1",
  "grade": "A",
  "weight": "45.50",
  "date": "2025-01-14",
  "ripeness_score": "87.00",
  "created_at": "2025-01-14T10:35:00Z",
  "updated_at": "2025-01-14T10:35:00Z"
}
```

### Step 4: Create Floating Test (Grade B)
```bash
curl -X POST http://localhost:8000/api/processing/floating/ \
  -H "Content-Type: application/json" \
  -d '{
    "harvest": "ED0711PA1",
    "grade": "B",
    "weight": 12.30
  }'
```

**Response:**
```json
{
  "grade_id": "GRB1401A00",
  "harvest": "ED0711PA1",
  "harvest_id": "ED0711PA1",
  "grade": "B",
  "weight": "12.30",
  "date": "2025-01-14",
  "ripeness_score": "87.00",
  "created_at": "2025-01-14T10:36:00Z",
  "updated_at": "2025-01-14T10:36:00Z"
}
```

### Step 5: View All Tests for Harvest
```bash
curl http://localhost:8000/api/processing/floating/by-harvest/ED0711PA1/
```

---

## Error Handling

### Validation Errors

**Example: Red cherries exceed sample size**
```http
POST /api/processing/ripeness/
Content-Type: application/json

{
  "harvest": "ED0711PA1",
  "sample_size": 100,
  "no_of_redcherry": 110
}
```

**Response (400 Bad Request):**
```json
{
  "no_of_redcherry": [
    "Number of red cherries (110) cannot exceed sample size (100)"
  ]
}
```

**Example: Duplicate ripeness test**
```http
POST /api/processing/ripeness/
Content-Type: application/json

{
  "harvest": "ED0711PA1",
  "sample_size": 100,
  "no_of_redcherry": 87
}
```

**Response (400 Bad Request):**
```json
{
  "harvest": [
    "ripeness with this harvest already exists."
  ]
}
```

**Example: Harvest doesn't exist**
```http
POST /api/processing/ripeness/
Content-Type: application/json

{
  "harvest": "INVALID123",
  "sample_size": 100,
  "no_of_redcherry": 87
}
```

**Response (400 Bad Request):**
```json
{
  "harvest": [
    "Invalid pk \"INVALID123\" - object does not exist."
  ]
}
```

---

## Testing with Python Requests

```python
import requests

BASE_URL = "http://localhost:8000/api/processing"

# Create Ripeness Test
ripeness_data = {
    "harvest": "ED0711PA1",
    "sample_size": 100,
    "no_of_redcherry": 87
}
response = requests.post(f"{BASE_URL}/ripeness/", json=ripeness_data)
print(response.json())

# Create Floating Test (Grade A)
floating_a_data = {
    "harvest": "ED0711PA1",
    "grade": "A",
    "weight": 45.50
}
response = requests.post(f"{BASE_URL}/floating/", json=floating_a_data)
print(response.json())

# Create Floating Test (Grade B)
floating_b_data = {
    "harvest": "ED0711PA1",
    "grade": "B",
    "weight": 12.30
}
response = requests.post(f"{BASE_URL}/floating/", json=floating_b_data)
print(response.json())

# Get all floating tests for harvest
response = requests.get(f"{BASE_URL}/floating/by-harvest/ED0711PA1/")
print(response.json())

# Get summary statistics
response = requests.get(f"{BASE_URL}/ripeness/summary/")
print(response.json())

response = requests.get(f"{BASE_URL}/floating/summary/")
print(response.json())
```

---

## Testing with JavaScript/React Native

```javascript
const BASE_URL = 'http://localhost:8000/api/processing';

// Create Ripeness Test
async function createRipenessTest() {
  const response = await fetch(`${BASE_URL}/ripeness/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      harvest: 'ED0711PA1',
      sample_size: 100,
      no_of_redcherry: 87
    })
  });

  const data = await response.json();
  console.log('Ripeness Test:', data);
  return data;
}

// Create Floating Test
async function createFloatingTest(grade, weight) {
  const response = await fetch(`${BASE_URL}/floating/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      harvest: 'ED0711PA1',
      grade: grade,
      weight: weight
    })
  });

  const data = await response.json();
  console.log(`Floating Test (Grade ${grade}):`, data);
  return data;
}

// Get Floating Tests by Harvest
async function getFloatingTestsByHarvest(harvestId) {
  const response = await fetch(`${BASE_URL}/floating/by-harvest/${harvestId}/`);
  const data = await response.json();
  console.log('Floating Tests:', data);
  return data;
}

// Usage
createRipenessTest();
createFloatingTest('A', 45.50);
createFloatingTest('B', 12.30);
getFloatingTestsByHarvest('ED0711PA1');
```

---

## Quick Reference

### Ripeness Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/processing/ripeness/` | List all ripeness tests |
| POST | `/api/processing/ripeness/` | Create new ripeness test |
| GET | `/api/processing/ripeness/{id}/` | Get specific test |
| PUT | `/api/processing/ripeness/{id}/` | Update test (full) |
| PATCH | `/api/processing/ripeness/{id}/` | Update test (partial) |
| DELETE | `/api/processing/ripeness/{id}/` | Delete test |
| GET | `/api/processing/ripeness/summary/` | Get statistics |

### Floating Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/processing/floating/` | List all floating tests |
| POST | `/api/processing/floating/` | Create new floating test |
| GET | `/api/processing/floating/{id}/` | Get specific test |
| PUT | `/api/processing/floating/{id}/` | Update test (full) |
| PATCH | `/api/processing/floating/{id}/` | Update test (partial) |
| DELETE | `/api/processing/floating/{id}/` | Delete test |
| GET | `/api/processing/floating/summary/` | Get statistics |
| GET | `/api/processing/floating/by-harvest/{id}/` | Get tests by harvest |

---

**Document Version:** 1.0
**Last Updated:** 2025-01-14
**Status:** Ready for Testing ✅
