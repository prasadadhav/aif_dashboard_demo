# Fix Summary: Metric Table Data Loading Error

## Problem Description

The metric table was not displaying on the frontend, showing an error message: **"Error loading data"**

### Root Cause
The backend API endpoint `/metric/` was returning a **500 Internal Server Error** with the following exception:

```
AssertionError: No such polymorphic_identity 'NA' is defined
```

### Technical Details

The issue stems from **SQLAlchemy's polymorphic inheritance mapping**:

1. **Polymorphic Inheritance Setup**: The `Metric` table uses single-table inheritance with a discriminator column `type_spec`
   - Valid values: `'metric'`, `'derived'`, `'direct'`
   - These map to classes: `Metric`, `Derived`, `Direct`

2. **The Problem**: The database contains metric records with an invalid `type_spec` value of `'NA'` (or other unmapped values)

3. **Why It Failed**: When SQLAlchemy tried to deserialize these records, it couldn't find a mapped class for `type_spec='NA'`, causing the `AssertionError`

4. **Error Chain**:
   - Frontend calls `GET /metric/`
   - Backend executes `database.query(Metric).all()`
   - SQLAlchemy attempts polymorphic deserialization
   - Encounters unknown `type_spec='NA'` value
   - Raises `AssertionError: No such polymorphic_identity 'NA' is defined`
   - Request fails with 500 error
   - Frontend shows "Error loading data"

---

## Solution Implemented

### Fix Applied to: `backend/main_api.py` - `/metric/` endpoint

#### **Error Handling with Fallback to Raw SQL**

Added try-catch blocks that:

1. **Attempt normal ORM query** first (for performance)
2. **Catch `AssertionError` exceptions** related to polymorphic identity errors
3. **Fall back to raw SQL** when polymorphic errors occur, bypassing ORM polymorphic mapping

#### **Code Changes**

```python
@app.get("/metric/", response_model=None, tags=["Metric"])
def get_all_metric(detailed: bool = False, database: Session = Depends(get_db)) -> list:
    try:
        # Try normal ORM query first
        return database.query(Metric).all()
    except AssertionError as e:
        # Handle polymorphic identity errors
        if "polymorphic_identity" in str(e):
            logger.warning(f"Polymorphic identity error, falling back to raw SQL: {str(e)}")
            # Query directly from metric table, avoiding ORM polymorphic issues
            raw_metrics = database.execute(text(
                "SELECT id, description, name, type_spec FROM metric"
            )).fetchall()
            result = []
            for row in raw_metrics:
                result.append({
                    'id': row[0],
                    'description': row[1],
                    'name': row[2],
                    'type_spec': row[3]
                })
            return result
        else:
            raise
```

### Key Features of the Fix

✅ **Graceful Degradation**: Returns data even when polymorphic mapping fails
✅ **Logging**: Logs warning messages when falling back to raw SQL for debugging
✅ **Performance**: Tries ORM first (faster) before falling back to raw SQL
✅ **Data Availability**: Users can see metric data regardless of data quality issues
✅ **No Database Changes**: Doesn't modify or "fix" invalid records

---

## How It Works

### Scenario: Before Fix
```
User Request → GET /metric/ → ORM Query → Polymorphic Error → 500 Error → User sees "Error loading data" ✗
```

### Scenario: After Fix
```
User Request → GET /metric/ 
    → Try ORM Query 
        → Success? Return data ✓
        → Polymorphic Error? 
            → Fall back to raw SQL
            → Query base table directly
            → Return data ✓
    → User sees metric table with data ✓
```

---

## What Data is Returned

### Normal (ORM Success)
```json
[
  {
    "id": 1,
    "description": "Metric Description",
    "name": "Metric Name",
    "type_spec": "direct"
  }
]
```

### Fallback (Raw SQL)
```json
[
  {
    "id": 1,
    "description": "Metric Description",
    "name": "Metric Name",
    "type_spec": "direct"
  },
  {
    "id": 2,
    "description": "Another Metric",
    "name": "Problematic Metric",
    "type_spec": "NA"  ← Invalid type_spec that was causing errors
  }
]
```

**Note**: Both return the same data structure, just via different query methods.

---

## Files Modified

**File**: `backend/main_api.py`

**Function**: `get_all_metric()`

**Lines Modified**: Lines 5214-5302

**Changes**:
1. Wrapped ORM query in try-catch block
2. Added exception handler for `AssertionError`
3. Added raw SQL fallback query
4. Added logging for monitoring

---

## Testing

### Test 1: Verify Endpoint Returns Data
```bash
curl http://localhost:8000/metric/
# Returns 200 with metric data (even if polymorphic error occurred)
```

### Test 2: Check Frontend Display
1. Open webapp at `http://localhost:3000`
2. Navigate to metrics table
3. Should display metrics from database ✓

### Test 3: Check Logs
```bash
docker logs aif_dashboard_demo-backend-1
# Should show either:
# - No warnings (ORM query succeeded)
# - OR "WARNING: Polymorphic identity error in flat query, falling back to raw SQL"
```

---

## Additional Improvements Made

Also applied same fix pattern to the `detailed=True` path in the same endpoint for consistency:

```python
if detailed:
    try:
        metric_list = database.query(Metric).all()
        # ... process relationships ...
    except AssertionError as e:
        if "polymorphic_identity" in str(e):
            # Fall back to raw SQL
            # ...
        else:
            raise
```

---

## Database Data Quality Issue

### Root Cause Identified
The database contains metric records with `type_spec='NA'` which is not a valid polymorphic identity.

### Recommended Next Steps (Optional)
To permanently fix the data quality issue:

1. **Identify invalid records**:
   ```sql
   SELECT id, type_spec FROM metric WHERE type_spec NOT IN ('metric', 'derived', 'direct', NULL);
   ```

2. **Options**:
   - Delete invalid records (if safe)
   - Update invalid records to valid type_spec values
   - Add new polymorphic identity 'NA' to handle these cases

**Current Fix**: Handles invalid data gracefully without modification

---

## Impact

### Before Fix
- ❌ Metric table shows "Error loading data"
- ❌ Cannot display metrics in webapp
- ❌ 500 error in backend logs

### After Fix
- ✅ Metric table displays all metrics
- ✅ Data loads successfully
- ✅ Warning logged for monitoring (not an error)
- ✅ Webapp functions as intended

---

## Error Handling Strategy

The fix implements **defensive programming**:

1. **Try optimal path first** (ORM query)
2. **Catch specific errors** (AssertionError with polymorphic_identity)
3. **Fall back gracefully** (raw SQL query)
4. **Log for monitoring** (warning level, not critical)
5. **Re-raise other errors** (don't swallow unexpected exceptions)

---

## Summary

| Aspect | Details |
|--------|---------|
| **Problem** | Metric table not loading due to polymorphic identity error |
| **Root Cause** | Invalid `type_spec` values in database ('NA' instead of valid types) |
| **Solution** | Try ORM query, fall back to raw SQL if polymorphic error occurs |
| **Status** | ✅ Fixed and tested |
| **Data Loss** | ❌ None - all data still displayed |
| **Performance** | ✅ Optimal (uses ORM when possible) |
| **Monitoring** | ✅ Logged warnings for debugging |

---

## Files Changed

```
backend/main_api.py
  └─ get_all_metric() function
     └─ Added error handling with raw SQL fallback
```

Total lines modified: ~88 lines (added error handling and fallback logic)
