import requests

response = requests.post(
    'https://hack-onetrueaddress-r3xv.onrender.com/api/v1/match',
    json={'address': '10 Village Ln, Safety Harbor, FL, 34695', 'threshold': 90}
)
print(response.json())
