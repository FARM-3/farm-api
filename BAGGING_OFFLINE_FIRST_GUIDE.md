# Bagging Module - Offline-First Frontend Guide

## Overview

The Bagging module is designed for **offline-first mobile app** architecture. The backend is a **simple CRUD API** that stores and retrieves data. **All business logic, validation, and calculations happen on the frontend.**

---

## Backend API Endpoints

### Base URL
```
/api/processing/bagging/
```

### 1. List All Bagging Records
```http
GET /api/processing/bagging/
```

**Response:**
```json
{
  "count": 150,
  "next": "http://api.example.com/api/processing/bagging/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "lot_id": "W46",
      "weight": 85.5,
      "moisture_content": 11.2,
      "no_of_bags": 5,
      "date": "2025-11-14T10:30:00Z",
      "outturn": null,
      "expected_outturn": null,
      "qr_code": null,
      "created_at": "2025-11-14T10:30:00Z",
      "updated_at": "2025-11-14T10:30:00Z"
    }
  ]
}
```

### 2. Create New Bagging Record
```http
POST /api/processing/bagging/
Content-Type: application/json

{
  "lot_id": "W46",
  "weight": 85.5,
  "moisture_content": 11.2,
  "no_of_bags": 5,
  "date": "2025-11-14T10:30:00Z",
  "outturn": 78.5,
  "expected_outturn": 80.0,
  "qr_code": null
}
```

**Response:** Returns the created record with `id`

### 3. Get Single Bagging Record
```http
GET /api/processing/bagging/{id}/
```

### 4. Update Bagging Record (Full Replace)
```http
PUT /api/processing/bagging/{id}/
Content-Type: application/json

{
  "lot_id": "W46",
  "weight": 85.5,
  "moisture_content": 11.2,
  "no_of_bags": 5,
  "date": "2025-11-14T10:30:00Z",
  "outturn": 78.5,
  "expected_outturn": 80.0,
  "qr_code": null
}
```

### 5. Update Bagging Record (Partial)
```http
PATCH /api/processing/bagging/{id}/
Content-Type: application/json

{
  "weight": 86.0,
  "no_of_bags": 6
}
```

### 6. Delete Bagging Record
```http
DELETE /api/processing/bagging/{id}/
```

---

## Data Model

### Bagging Record Fields

| Field | Type | Writable | Description |
|-------|------|----------|-------------|
| `id` | Integer | No | Primary key (auto-generated) |
| `lot_id` | String(100) | Yes | Lot ID from Drying (references W01-W52) |
| `weight` | Decimal | Yes | Weight in kilograms (≥ 0.01) |
| `moisture_content` | Decimal | Yes | Moisture content percentage (0-100) |
| `no_of_bags` | Integer | Yes | Total number of bags (≥ 1) |
| `date` | DateTime | Yes | Bagging date/time |
| `outturn` | Decimal | Yes | Measured outturn percentage (calculated on frontend) |
| `expected_outturn` | Decimal | Yes | Expected outturn percentage (calculated on frontend) |
| `qr_code` | String(255) | Yes | QR code payload (leave blank for future) |
| `created_at` | DateTime | No | Record creation timestamp |
| `updated_at` | DateTime | No | Record last update timestamp |

---

## Frontend Logic & Calculations

### 1. Lot ID Selection
The user **selects an existing lot_id** from the Drying records:
```javascript
// Fetch available lots
const dryingLots = await fetch('/api/processing/drying/')
  .then(r => r.json())
  .then(data => [...new Set(data.results.map(r => r.lot_id))]);

// User selects: "W46"
// This is stored directly in the bagging record
```

### 2. Average Weight Per Bag (Computed Field)
Display only - do NOT send to backend:
```javascript
function calculateAverageWeightPerBag(weight, numberOfBags) {
  if (numberOfBags <= 0) return 0;
  return (weight / numberOfBags).toFixed(2);
}

// Example:
// weight = 85.5 kg, no_of_bags = 5
// average_weight_per_bag = 85.5 / 5 = 17.1 kg
```

### 3. Outturn Calculation
**Outturn** = percentage of final weight relative to starting weight

Pull the first drying entry for the lot_id, then calculate:
```javascript
async function calculateOutturn(lotId, baggingWeight) {
  // Get first drying entry for this lot
  const dryingRecords = await fetch(`/api/processing/drying/?lot_id=${lotId}`)
    .then(r => r.json())
    .then(data => data.results.sort((a, b) => new Date(a.date) - new Date(b.date)));

  if (!dryingRecords.length) return null;

  const firstDryingWeight = dryingRecords[0].weight;
  const outturn = ((baggingWeight / firstDryingWeight) * 100).toFixed(2);

  return parseFloat(outturn);
}

// Example:
// First drying weight = 100 kg
// Bagging weight = 78.5 kg
// outturn = (78.5 / 100) * 100 = 78.5%
```

### 4. Expected Outturn Calculation
**Expected Outturn** = based on final moisture content vs. standard target (e.g., 12%)

```javascript
function calculateExpectedOutturn(moistureContent) {
  // Typical coffee dries from ~45% to 11-12% moisture
  // Simple formula: Higher moisture = higher expected outturn
  const targetMoisture = 12; // Industry standard
  const startingMoisture = 45; // Approximate cherry moisture

  // Expected outturn = weight loss ratio
  // Formula: ((starting_moisture - final_moisture) / starting_moisture) * base_weight

  // Simplified:
  // If moisture = 12%, outturn ≈ 60-65% (baseline)
  // If moisture = 11%, outturn ≈ 62-67%
  // If moisture = 10%, outturn ≈ 64-69%

  const baseOutturn = 62; // Baseline at 12% moisture
  const adjustment = (targetMoisture - moistureContent) * 0.5; // 0.5% per 1% moisture difference

  return (baseOutturn + adjustment).toFixed(2);
}

// Example:
// moisture_content = 11.2%
// target_moisture = 12%
// expected_outturn = 62 + ((12 - 11.2) * 0.5) = 62.4%
```

**Note:** The exact formula depends on your coffee processing data. Work with your team to refine this based on historical data.

---

## Frontend Implementation Example (React/React Native)

### Form Component Structure
```javascript
import React, { useState, useEffect } from 'react';

const BaggingForm = () => {
  const [formData, setFormData] = useState({
    lot_id: '',
    weight: '',
    moisture_content: '',
    no_of_bags: '',
    date: new Date().toISOString(),
    outturn: null,
    expected_outturn: null,
    qr_code: null
  });

  const [availableLots, setAvailableLots] = useState([]);
  const [errors, setErrors] = useState({});

  useEffect(() => {
    fetchAvailableLots();
  }, []);

  // Fetch lots from Drying
  const fetchAvailableLots = async () => {
    try {
      const response = await fetch('/api/processing/drying/');
      const data = await response.json();
      const uniqueLots = [...new Set(data.results.map(r => r.lot_id))];
      setAvailableLots(uniqueLots);
    } catch (error) {
      console.error('Failed to fetch lots:', error);
    }
  };

  // Validate form data
  const validateForm = () => {
    const newErrors = {};

    if (!formData.lot_id) newErrors.lot_id = 'Lot ID is required';
    if (!formData.weight || parseFloat(formData.weight) < 0.01) {
      newErrors.weight = 'Weight must be at least 0.01 kg';
    }
    if (!formData.moisture_content || parseFloat(formData.moisture_content) < 0 || parseFloat(formData.moisture_content) > 100) {
      newErrors.moisture_content = 'Moisture content must be 0-100%';
    }
    if (!formData.no_of_bags || parseInt(formData.no_of_bags) < 1) {
      newErrors.no_of_bags = 'Number of bags must be at least 1';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Calculate derived fields
  const calculateDerivedFields = async () => {
    const weight = parseFloat(formData.weight);
    const moisture = parseFloat(formData.moisture_content);
    const bags = parseInt(formData.no_of_bags);

    if (isNaN(weight) || isNaN(moisture) || isNaN(bags)) return;

    // Calculate outturn
    const outturn = await calculateOutturn(formData.lot_id, weight);

    // Calculate expected outturn
    const expectedOutturn = calculateExpectedOutturn(moisture);

    setFormData(prev => ({
      ...prev,
      outturn: outturn ? parseFloat(outturn) : null,
      expected_outturn: parseFloat(expectedOutturn)
    }));
  };

  // Handle input changes
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  // Handle blur on key fields to trigger calculations
  const handleFieldBlur = async (fieldName) => {
    if (['weight', 'moisture_content', 'no_of_bags', 'lot_id'].includes(fieldName)) {
      await calculateDerivedFields();
    }
  };

  // Submit form
  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) {
      alert('Please fix validation errors');
      return;
    }

    try {
      const response = await fetch('/api/processing/bagging/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        const data = await response.json();
        alert(`Bagging record created: ID ${data.id}`);
        // Reset form or navigate
      } else {
        const error = await response.json();
        alert(`Error: ${JSON.stringify(error)}`);
      }
    } catch (error) {
      console.error('Submit failed:', error);
      alert('Failed to save bagging record');
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label>Lot ID *</label>
        <select
          name="lot_id"
          value={formData.lot_id}
          onChange={handleChange}
          onBlur={() => handleFieldBlur('lot_id')}
        >
          <option value="">Select a lot</option>
          {availableLots.map(lot => (
            <option key={lot} value={lot}>{lot}</option>
          ))}
        </select>
        {errors.lot_id && <span className="error">{errors.lot_id}</span>}
      </div>

      <div>
        <label>Weight (kg) *</label>
        <input
          type="number"
          name="weight"
          value={formData.weight}
          onChange={handleChange}
          onBlur={() => handleFieldBlur('weight')}
          step="0.01"
          min="0.01"
        />
        {errors.weight && <span className="error">{errors.weight}</span>}
      </div>

      <div>
        <label>Moisture Content (%) *</label>
        <input
          type="number"
          name="moisture_content"
          value={formData.moisture_content}
          onChange={handleChange}
          onBlur={() => handleFieldBlur('moisture_content')}
          step="0.01"
          min="0"
          max="100"
        />
        {errors.moisture_content && <span className="error">{errors.moisture_content}</span>}
      </div>

      <div>
        <label>Number of Bags *</label>
        <input
          type="number"
          name="no_of_bags"
          value={formData.no_of_bags}
          onChange={handleChange}
          onBlur={() => handleFieldBlur('no_of_bags')}
          min="1"
        />
        {errors.no_of_bags && <span className="error">{errors.no_of_bags}</span>}
      </div>

      <div>
        <label>Date & Time</label>
        <input
          type="datetime-local"
          name="date"
          value={formData.date.slice(0, 16)}
          onChange={(e) => setFormData(prev => ({
            ...prev,
            date: new Date(e.target.value).toISOString()
          }))}
        />
      </div>

      <div className="computed-fields">
        <div>
          <label>Average Weight per Bag (Display Only)</label>
          <span>
            {formData.no_of_bags && formData.weight
              ? (parseFloat(formData.weight) / parseInt(formData.no_of_bags)).toFixed(2)
              : '-'} kg
          </span>
        </div>

        <div>
          <label>Outturn (%) *</label>
          <span>{formData.outturn !== null ? formData.outturn : 'Calculating...'}</span>
        </div>

        <div>
          <label>Expected Outturn (%) *</label>
          <span>{formData.expected_outturn !== null ? formData.expected_outturn : 'Calculating...'}</span>
        </div>
      </div>

      <div>
        <label>QR Code (Optional)</label>
        <input
          type="text"
          name="qr_code"
          value={formData.qr_code || ''}
          onChange={handleChange}
          placeholder="QR code payload (leave blank for now)"
        />
      </div>

      <button type="submit">Save Bagging Record</button>
    </form>
  );
};

export default BaggingForm;
```

---

## Offline Sync Strategy

### Local Storage Structure
```javascript
// Store bagging records locally
const baggingQueue = [
  {
    id: 'local_1',
    lot_id: 'W46',
    weight: 85.5,
    moisture_content: 11.2,
    no_of_bags: 5,
    date: '2025-11-14T10:30:00Z',
    outturn: 78.5,
    expected_outturn: 80.0,
    qr_code: null,
    synced: false,  // Track sync status
    createdAt: '2025-11-14T10:30:00Z'
  }
];

// Save to local storage
localStorage.setItem('baggingQueue', JSON.stringify(baggingQueue));
```

### Sync Process (when online)
```javascript
async function syncBaggingRecords() {
  const queue = JSON.parse(localStorage.getItem('baggingQueue') || '[]');
  const unsyncedRecords = queue.filter(r => !r.synced);

  for (const record of unsyncedRecords) {
    try {
      // Check if record has server ID (was previously synced)
      if (record.id && !record.id.startsWith('local_')) {
        // Update existing
        await fetch(`/api/processing/bagging/${record.id}/`, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(record)
        });
      } else {
        // Create new
        const response = await fetch('/api/processing/bagging/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(record)
        });
        const saved = await response.json();
        record.id = saved.id;  // Update with server ID
      }

      record.synced = true;
    } catch (error) {
      console.error('Failed to sync bagging record:', error);
      // Keep in queue for retry
    }
  }

  // Save updated queue
  localStorage.setItem('baggingQueue', JSON.stringify(queue));
}

// Call on app start or periodically
if (navigator.onLine) {
  syncBaggingRecords();
}
```

---

## Best Practices

### 1. **Do All Validation on Frontend**
- Check moisture_content is 0-100%
- Check weight is > 0
- Check no_of_bags is ≥ 1
- Check lot_id is selected
- Don't rely on backend validation

### 2. **Calculate on Frontend**
- Average weight per bag (display only)
- Outturn percentage
- Expected outturn percentage
- These should all happen before submission

### 3. **Handle Network Failures Gracefully**
- Save to local storage before sending
- Mark as pending/synced
- Retry on next connection
- Show sync status to user

### 4. **Keep QR Code Flexible**
- Don't enforce a specific format yet
- Allow users to leave it blank
- Can expand format later without code changes

### 5. **Use ISO 8601 for Dates**
- Always send dates as: `"2025-11-14T10:30:00Z"`
- Parse user input (datetime-local) to ISO format
- Store in UTC for consistency

---

## Error Handling

### Field Validation Errors
```javascript
const errors = {
  lot_id: 'Lot ID is required',
  weight: 'Weight must be at least 0.01 kg',
  moisture_content: 'Moisture content must be 0-100%',
  no_of_bags: 'Number of bags must be at least 1'
};
```

### Network Errors
```javascript
try {
  await fetch('/api/processing/bagging/', {...});
} catch (error) {
  // Store locally and mark for sync
  // Show "Will sync when connection restored"
  console.error('Network error:', error);
}
```

### Server Errors
```javascript
if (response.status === 400) {
  const error = await response.json();
  // Display field-level errors to user
  console.error('Validation failed:', error);
} else if (response.status >= 500) {
  // Server error - queue for retry
}
```

---

## Summary

The Bagging module API is **dead simple**:
- **GET** `/api/processing/bagging/` - List all records
- **POST** `/api/processing/bagging/` - Create new record
- **PUT** `/api/processing/bagging/{id}/` - Full update
- **PATCH** `/api/processing/bagging/{id}/` - Partial update
- **DELETE** `/api/processing/bagging/{id}/` - Delete

**Everything else is frontend responsibility**: validation, calculations, offline storage, and sync logic.

This keeps the backend lightweight and gives your frontend complete control over business logic.
