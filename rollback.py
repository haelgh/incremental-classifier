import boto3
import time
from sagemaker import Session
import os
from dotenv import load_dotenv

load_dotenv()

ENDPOINT_NAME = os.getenv('SAGEMAKER_ENDPOINT_NAME')
REGION = os.getenv('AWS_REGION')

client = boto3.client('sagemaker', region_name=REGION)

def rollback():
    print(f"Checking endpoint: {ENDPOINT_NAME}...")
    
    configs = client.list_endpoint_configs(
        SortBy='CreationTime', SortOrder='Descending', NameContains='news-model'
    )
    
    if len(configs['EndpointConfigs']) < 2:
        print("Not enough history to rollback! Need at least 2 configurations.")
        return

    current_config = configs['EndpointConfigs'][0]['EndpointConfigName']
    previous_config = configs['EndpointConfigs'][1]['EndpointConfigName']
    
    print(f"Current Config: {current_config}")
    print(f"Rolling back to: {previous_config} ...")
    try:
        client.update_endpoint(
            EndpointName=ENDPOINT_NAME,
            EndpointConfigName=previous_config
        )
        print("Rollback initiated! System is updating endpoint to previous version.")
        print("Status: Updating...")
    except Exception as e:
        print(f"Rollback failed: {e}")

if __name__ == "__main__":
    rollback()