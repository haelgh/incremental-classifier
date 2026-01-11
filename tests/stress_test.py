import requests
import time
import random

API_URL = "http://127.0.0.1:8000/predict"

print(">>> STARTING STRESS TEST VIA FASTAPI")

for i in range(5):
    try:
        resp = requests.post(API_URL, json={"text": "New computer processor released"})
        print(f"Normal: {resp.status_code} | {resp.json()}")
    except Exception as e:
        print(f"Is server running? {e}")
    time.sleep(1)

print("\n>>> SIMULATING ERRORS")
for i in range(10):
    try:
        resp = requests.post(API_URL, json={"text": ""}) 
        print(f"Attack: {resp.status_code}")
    except:
        pass
    time.sleep(0.5)