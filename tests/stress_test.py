import boto3
import time
import json
import random
import os
from dotenv import load_dotenv

load_dotenv()
REGION = os.getenv('AWS_REGION', 'eu-north-1')
ENDPOINT_NAME = os.getenv('SAGEMAKER_ENDPOINT_NAME')

client = boto3.client('sagemaker-runtime', region_name=REGION)

print(f">>> STARTING STRESS TEST on {ENDPOINT_NAME}")

print("Sending HEALTHY traffic (10 requests)...")
good_payload = {"source": "BBC", "title": "Technology and AI are growing fast"}

for i in range(10):
    try:
        response = client.invoke_endpoint(
            EndpointName=ENDPOINT_NAME,
            ContentType='application/json',
            Body=json.dumps(good_payload)
        )
        print(f"OK: {response['ResponseMetadata']['HTTPStatusCode']}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    time.sleep(0.5)

print("\n>>> SIMULATING FAILURE (Sending garbage data to trigger Alarm)...")
for i in range(10):
    try:
        client.invoke_endpoint(
            EndpointName=ENDPOINT_NAME,
            ContentType='application/json',
            Body='{"broken_json": '
        )
    except Exception as e:
        print(f"Error triggered successfully ({i+1}/10)")
        time.sleep(1)

print("\nTests finished. Wait 2-3 minutes and check CloudWatch Alarms!")