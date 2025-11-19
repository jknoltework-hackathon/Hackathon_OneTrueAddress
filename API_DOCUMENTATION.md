# OneTrueAddress API Documentation

Version: 1.0  
Base URL: `http://your-server:5000/api/v1`

## Overview

The OneTrueAddress API provides programmatic access to address matching, consolidation, and database update functionality. All endpoints accept and return JSON data.

## Authentication

Currently, the API does not require authentication. **Note:** You should implement authentication before deploying to production.

## Content Type

All POST requests must include:
```
Content-Type: application/json
```

## Endpoints

### 1. Health Check

Check if the API is running.

**Endpoint:** `GET /api/v1/health`

**Response:**
```json
{
  "status": "ok",
  "version": "1.0",
  "service": "OneTrueAddress API"
}
```

**Example:**
```bash
curl http://localhost:5000/api/v1/health
```

---

### 2. Match Address

Match an input address against Golden Source and Internal databases using fuzzy matching and AI analysis.

**Endpoint:** `POST /api/v1/match`

**Request Body:**
```json
{
  "address": "123 Main St, Anytown, FL 12345",
  "threshold": 90
}
```

**Parameters:**
- `address` (string, required): The address to match
- `threshold` (number, optional): Minimum similarity score (75-100). Default: 90

**Success Response (200):**
```json
{
  "success": true,
  "match_found": true,
  "confidence": 95.5,
  "similarity_score": 95.5,
  "input_address": "123 Main St, Anytown, FL 12345",
  "matched_address": {
    "address1": "123 Main Street",
    "address2": "",
    "City": "Anytown",
    "state": "FL",
    "zipcode": "12345",
    "MasterAddress": "123 Main Street, Anytown, FL 12345",
    "_similarity_score": 95.5,
    "_source_table": "team_cool_and_gang.pinellas_fl",
    "_source_type": "golden_source"
  },
  "golden_source_matches": [
    {
      "address1": "123 Main Street",
      "MasterAddress": "123 Main Street, Anytown, FL 12345",
      "_similarity_score": 95.5
    }
  ],
  "internal_matches": [
    {
      "Address": "123 Main St",
      "MasterAddress": "123 Main St, Anytown, FL 12345",
      "_similarity_score": 92.0,
      "Bad Type": "Abbreviation",
      "Active Customer": "Y",
      "Media": "Fiber"
    }
  ],
  "total_golden_source": 1,
  "total_internal": 1,
  "has_golden_source": true,
  "has_internal": true,
  "reasoning": "High confidence match found with 95.5% similarity",
  "business_rule_exception": false,
  "confidence_threshold": 90.0,
  "candidates_searched": 15,
  "search_method": "fuzzy_match_with_ai",
  "source_table": "team_cool_and_gang.pinellas_fl",
  "source_type": "golden_source"
}
```

**No Match Response (200):**
```json
{
  "success": true,
  "match_found": false,
  "confidence": 0,
  "reasoning": "No addresses found matching the search criteria",
  "candidates_searched": 0
}
```

**Error Response (400/500):**
```json
{
  "success": false,
  "error": "Address is required"
}
```

**Example:**
```bash
curl -X POST http://localhost:5000/api/v1/match \
  -H "Content-Type: application/json" \
  -d '{
    "address": "123 Main St, Anytown, FL 12345",
    "threshold": 90
  }'
```

**Python Example:**
```python
import requests

response = requests.post(
    'http://localhost:5000/api/v1/match',
    json={
        'address': '123 Main St, Anytown, FL 12345',
        'threshold': 90
    }
)

data = response.json()
if data['success'] and data['match_found']:
    print(f"Match found with {data['confidence']}% confidence")
    print(f"Master Address: {data['matched_address']['MasterAddress']}")
else:
    print("No match found")
```

---

### 3. Consolidate Records

Consolidate multiple internal records with a Golden Source address.

**Endpoint:** `POST /api/v1/consolidate`

**Request Body:**
```json
{
  "internal_matches": [
    {
      "Address": "123 Main St",
      "City": "Anytown",
      "State": "FL",
      "Zipcode": "12345",
      "MasterAddress": "123 Main St, Anytown, FL 12345",
      "Bad Type": "Abbreviation",
      "Active Customer": "Y",
      "Media": "Copper",
      "Exclusion": "N",
      "Engineering Review": "N"
    },
    {
      "Address": "123 Main Street",
      "City": "Anytown",
      "State": "FL",
      "Zipcode": "12345",
      "MasterAddress": "123 Main Street, Anytown, FL 12345",
      "Bad Type": "Duplicate",
      "Active Customer": "N",
      "Media": "Fiber",
      "Exclusion": "N",
      "Engineering Review": "Y"
    }
  ],
  "golden_source_address": {
    "address1": "123 Main Street",
    "address2": "",
    "Mailing City": "Anytown",
    "state": "FL",
    "zipcode": "12345",
    "MasterAddress": "123 Main Street, Anytown, FL 12345"
  },
  "scenario": 1
}
```

**Parameters:**
- `internal_matches` (array, required): Array of internal records to consolidate
- `golden_source_address` (object, required): Golden Source address (authoritative)
- `scenario` (number, optional): Scenario type (1=Multiple Matches, 2=Single Mismatch, 3=No Internal). Default: 1

**Success Response (200):**
```json
{
  "success": true,
  "consolidated_record": {
    "Address": "123 Main Street",
    "City": "Anytown",
    "State": "FL",
    "Zipcode": "12345",
    "MasterAddress": "123 Main Street, Anytown, FL 12345",
    "Bad Type": "Abbreviation; Duplicate",
    "Active Customer": "Y",
    "Media": "Fiber",
    "Exclusion": "N",
    "Engineering Review": "Y"
  },
  "message": "Consolidated 2 records successfully"
}
```

**Error Response (400):**
```json
{
  "success": false,
  "error": "Multiple Active Customer records found. Manual review required.",
  "requires_manual_review": true
}
```

**Example:**
```bash
curl -X POST http://localhost:5000/api/v1/consolidate \
  -H "Content-Type: application/json" \
  -d @consolidate_request.json
```

---

### 4. Push Updates

Consolidate records and push to internal_updates table.

**Endpoint:** `POST /api/v1/push_updates`

**Request Body:**
Same as `/consolidate` endpoint

**Success Response (200):**
```json
{
  "success": true,
  "message": "Record successfully pushed to team_cool_and_gang.internal_updates",
  "consolidated_record": {
    "Address": "123 Main Street",
    "City": "Anytown",
    "State": "FL",
    "Zipcode": "12345",
    "MasterAddress": "123 Main Street, Anytown, FL 12345",
    "Bad Type": "Abbreviation; Duplicate",
    "Active Customer": "Y",
    "Media": "Fiber"
  }
}
```

**Example:**
```python
import requests

response = requests.post(
    'http://localhost:5000/api/v1/push_updates',
    json={
        'internal_matches': internal_records,
        'golden_source_address': golden_address,
        'scenario': 1
    }
)

result = response.json()
if result['success']:
    print(f"✓ {result['message']}")
```

---

### 5. Write to Internal

Write a Golden Source record to internal_updates table (when no internal match exists).

**Endpoint:** `POST /api/v1/write_to_internal`

**Request Body:**
```json
{
  "golden_source_record": {
    "address1": "123 Main Street",
    "address2": "",
    "Mailing City": "Anytown",
    "state": "FL",
    "zipcode": "12345",
    "MasterAddress": "123 Main Street, Anytown, FL 12345",
    "last_edited_date": "2024-01-15"
  }
}
```

**Parameters:**
- `golden_source_record` (object, required): Golden Source record to write

**Success Response (200):**
```json
{
  "success": true,
  "message": "Record successfully pushed to team_cool_and_gang.internal_updates",
  "written_record": {
    "Address": "123 Main Street",
    "City": "Anytown",
    "State": "FL",
    "Zipcode": "12345",
    "MasterAddress": "123 Main Street, Anytown, FL 12345"
  }
}
```

---

### 6. Time Saved

Get total time saved by the system.

**Endpoint:** `GET /api/v1/time_saved`

**Success Response (200):**
```json
{
  "success": true,
  "hours_saved": 12.5
}
```

**Example:**
```bash
curl http://localhost:5000/api/v1/time_saved
```

---

## Error Handling

All endpoints return errors in the following format:

```json
{
  "success": false,
  "error": "Error message description"
}
```

**Common HTTP Status Codes:**
- `200` - Success
- `400` - Bad Request (invalid input)
- `500` - Internal Server Error

---

## Rate Limiting

Currently, there is no rate limiting implemented. Consider adding rate limiting in production.

---

## Example Workflow

### Complete Address Matching and Update Flow

```python
import requests

BASE_URL = "http://localhost:5000/api/v1"

# Step 1: Match an address
match_response = requests.post(
    f"{BASE_URL}/match",
    json={
        "address": "123 Main St, Anytown, FL 12345",
        "threshold": 90
    }
)

match_data = match_response.json()

if not match_data['success'] or not match_data['match_found']:
    print("No match found")
    exit()

print(f"✓ Match found: {match_data['confidence']}% confidence")

# Step 2: Check if update is needed
if (match_data['total_internal'] > 1 or 
    (match_data['total_internal'] == 1 and 
     match_data['has_golden_source'] and
     match_data['internal_matches'][0]['MasterAddress'] != 
     match_data['matched_address']['MasterAddress'])):
    
    print("Update needed - pushing consolidated record...")
    
    # Step 3: Push updates
    update_response = requests.post(
        f"{BASE_URL}/push_updates",
        json={
            "internal_matches": match_data['internal_matches'],
            "golden_source_address": match_data['matched_address'],
            "scenario": 1 if match_data['total_internal'] > 1 else 2
        }
    )
    
    update_data = update_response.json()
    
    if update_data['success']:
        print(f"✓ {update_data['message']}")
    else:
        print(f"✗ Error: {update_data['error']}")

# Step 4: Check time saved
time_response = requests.get(f"{BASE_URL}/time_saved")
time_data = time_response.json()
print(f"Total time saved: {time_data['hours_saved']} hours")
```

---

## Testing

Use the following curl command to test the API:

```bash
# Test health check
curl http://localhost:5000/api/v1/health

# Test address matching
curl -X POST http://localhost:5000/api/v1/match \
  -H "Content-Type: application/json" \
  -d '{"address": "123 Main St, Anytown, FL 12345", "threshold": 90}'

# Test with Python
python -c "
import requests
r = requests.post('http://localhost:5000/api/v1/match', 
                  json={'address': '123 Main St, Anytown, FL 12345'})
print(r.json())
"
```

---

## Notes

1. **Database Connection**: Ensure database credentials are properly configured in `.env` file
2. **Claude API**: AI analysis requires valid `CLAUDE_API_KEY` in environment variables
3. **Performance**: Large address datasets may take several seconds to process
4. **Thread Safety**: The current implementation uses a global agent instance. Consider connection pooling for high-concurrency scenarios.

---

## Support

For issues or questions, refer to the main README.md or contact your system administrator.

