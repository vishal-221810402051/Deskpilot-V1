import requests


url = "http://127.0.0.1:8765/gesture"

payload = {
    "gesture": "swipe_right_to_left"
}

response = requests.post(url, json=payload, timeout=5)

print(response.status_code)
print(response.json())
