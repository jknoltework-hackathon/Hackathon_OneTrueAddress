import requests

# Test the API endpoint
response = requests.post(
    'https://hack-onetrueaddress-r3xv.onrender.com/api/v1/match',
    json={'address': '10 Village Ln, Safety Harbor, FL, 34695', 'threshold': 70}
)

print(f"Status Code: {response.status_code}")
print(f"Content-Type: {response.headers.get('Content-Type', 'Unknown')}")
print(f"Response Text (first 500 chars):\n{response.text[:500]}")

# Try to parse JSON if possible
try:
    print(f"\nJSON Response:\n{response.json()}")
except Exception as e:
    print(f"\nFailed to parse JSON: {e}")
