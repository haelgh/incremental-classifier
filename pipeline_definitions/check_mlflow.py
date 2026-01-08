import os
import boto3
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(dotenv_path)
region = os.getenv('AWS_REGION', 'eu-north-1')

sm_client = boto3.client('sagemaker', region_name=region)

server_name = "news-mlflow-server"

try:
    response = sm_client.describe_mlflow_tracking_server(
        TrackingServerName=server_name
    )
    
    status = response['TrackingServerStatus']
    print(f"Server status MLflow: {status}")

    if status == 'Created':
        tracking_url = response['TrackingServerUrl']
        print(f"\n URL for code:")
        print(f"{tracking_url}")
    
    elif status == 'Creating':
        print("\n Server is still being created.")
    
    else:
        print(f"\nSomething went wrong. Status: {status}")

except Exception as e:
    print(f" Error: {e}")