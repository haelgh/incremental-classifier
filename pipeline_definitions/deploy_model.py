import os
import boto3
import sagemaker
from sagemaker.sklearn.model import SKLearnModel
from dotenv import load_dotenv
from datetime import datetime

MODEL_DATA_URL = os.environ.get('MODEL_DATA_URL')

if not MODEL_DATA_URL:
    print("Running locally? Loading .env file...")
    load_dotenv()
    MODEL_DATA_URL = os.getenv('MODEL_DATA_URL')

ROLE = os.environ.get('AWS_ROLE_ARN') or os.getenv('AWS_ROLE_ARN')
REGION = os.environ.get('AWS_REGION') or os.getenv('AWS_REGION', 'eu-north-1')
ENDPOINT_NAME = "news-classifier-endpoint"

if not MODEL_DATA_URL:
    raise ValueError("ERROR: MODEL_DATA_URL not found neither in Environment nor in .env file!")

boto_session = boto3.Session(region_name=REGION)
sagemaker_session = sagemaker.Session(boto_session=boto_session)
sm_client = boto_session.client('sagemaker')

print(f"--- Starting Deployment Process ---")
print(f"Model Artifact: {MODEL_DATA_URL}")
print(f"Target Endpoint: {ENDPOINT_NAME}")

print(f"Checking for old resources...")

try:
    sm_client.delete_endpoint(EndpointName=ENDPOINT_NAME)
    print(f"  - Old endpoint deleted.")
except:
    pass

try:
    sm_client.delete_endpoint_config(EndpointConfigName=ENDPOINT_NAME)
    print(f"  - Old endpoint configuration deleted.")
except:
    pass

model = SKLearnModel(
    model_data=MODEL_DATA_URL,
    role=ROLE,
    entry_point='inference.py',
    source_dir='app',
    framework_version='1.0-1',
    py_version='py3',
    sagemaker_session=sagemaker_session,
    name=f"news-model-{datetime.now().strftime('%H-%M-%S')}"
)

print(f"Deploying new endpoint...")
try:
    predictor = model.deploy(
        initial_instance_count=1,
        instance_type='ml.m5.large',
        endpoint_name=ENDPOINT_NAME,
        wait=True
    )
    print(f"\nSUCCESS! Deployment initiated.")
    print(f"Endpoint '{ENDPOINT_NAME}' is now in 'Creating' status.")
    print(f"Check progress here: https://{REGION}.console.aws.amazon.com/sagemaker/home?region={REGION}#/endpoints")
except Exception as e:
    print(f"\nCritical Error: {e}")