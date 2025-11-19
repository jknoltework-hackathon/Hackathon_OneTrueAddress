# OneTrueAddress API - Quick Reference

## Base URL
```
http://localhost:5000/api/v1
```

## Quick Start

### 1. Health Check
```bash
curl http://localhost:5000/api/v1/health
```

### 2. Match Address
```bash
curl -X POST http://localhost:5000/api/v1/match \
  -H "Content-Type: application/json" \
  -d '{"address": "123 Main St, City, FL 12345", "threshold": 90}'
```

### 3. Python Example
```python
import requests

# Match address
r = requests.post('http://localhost:5000/api/v1/match', 
                  json={'address': '123 Main St, City, FL 12345'})
result = r.json()

if result['match_found']:
    print(f"Match: {result['matched_address']['MasterAddress']}")
    print(f"Confidence: {result['confidence']}%")
```

## All Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/health` | Health check |
| POST | `/api/v1/match` | Match address |
| POST | `/api/v1/consolidate` | Consolidate records |
| POST | `/api/v1/push_updates` | Push updates to DB |
| POST | `/api/v1/write_to_internal` | Write Golden Source to internal |
| GET | `/api/v1/time_saved` | Get total time saved |

## Common Requests

### Match Address
```json
POST /api/v1/match
{
  "address": "123 Main St, City, FL 12345",
  "threshold": 90
}
```

### Push Updates
```json
POST /api/v1/push_updates
{
  "internal_matches": [...],
  "golden_source_address": {...},
  "scenario": 1
}
```

## Common Responses

### Success
```json
{
  "success": true,
  "match_found": true,
  "confidence": 95.5,
  "matched_address": {...}
}
```

### Error
```json
{
  "success": false,
  "error": "Error message"
}
```

## Status Codes
- `200` - Success
- `400` - Bad Request
- `500` - Server Error

## Testing
```bash
# Run test suite
python test_api.py

# Test specific address
python test_api.py "123 Main St, City, FL 12345"

# Test with custom threshold
python test_api.py "123 Main St, City, FL 12345" 85
```

## Full Documentation
See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for complete details.

