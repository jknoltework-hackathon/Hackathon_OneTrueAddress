"""Test script for local API endpoints."""
import requests
import json

BASE_URL = 'http://localhost:5000'

print("=" * 60)
print("Testing OneTrueAddress API - LOCAL")
print("=" * 60)

# Test 1: Health Check
print("\n1. Testing Health Check Endpoint...")
try:
    response = requests.get(f'{BASE_URL}/api/v1/health')
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
except Exception as e:
    print(f"   ERROR: {e}")

# Test 2: Match Address
print("\n2. Testing Match Address Endpoint...")
try:
    response = requests.post(
        f'{BASE_URL}/api/v1/match',
        json={'address': '10 Village Ln, Safety Harbor, FL, 34695', 'threshold': 90}
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Success: {data.get('success')}")
        print(f"   Match Found: {data.get('match_found')}")
        print(f"   Confidence: {data.get('confidence')}")
    else:
        print(f"   Error: {response.text[:200]}")
except Exception as e:
    print(f"   ERROR: {e}")

print("\n" + "=" * 60)
print("Local API Test Complete")
print("=" * 60)

