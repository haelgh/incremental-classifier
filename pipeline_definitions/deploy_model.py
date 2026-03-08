import os
import boto3
import sagemaker
from sagemaker.huggingface.model import HuggingFaceModel
from dotenv import load_dotenv
from datetime import datetime

print("Loading .env file...")
load_dotenv()

MODEL_DATA_URL = os.environ.get('MODEL_DATA_URL')

if not MODEL_DATA_URL:
    print("Running locally? Loading .env file...")
    load_dotenv()
    MODEL_DATA_URL = os.getenv('MODEL_DATA_URL')

ROLE = os.environ.get('AWS_ROLE_ARN') or os.getenv('AWS_ROLE_ARN')
REGION = os.environ.get('AWS_REGION') or os.getenv('AWS_REGION', 'eu-north-1')
ENDPOINT_NAME = "news-classifier-endpoint"
MODEL_DATA_URL = os.getenv('MODEL_DATA_URL')

if not MODEL_DATA_URL or not ROLE:
    raise ValueError("Критична помилка: не знайдено MODEL_DATA_URL або AWS_ROLE_ARN")

boto_session = boto3.Session(region_name=REGION)
sagemaker_session = sagemaker.Session(boto_session=boto_session)
sm_client = boto_session.client('sagemaker')

print(f"--- Розгортання моделі ---")
print(f"Модель: {MODEL_DATA_URL}")

try:
    sm_client.delete_endpoint(EndpointName=ENDPOINT_NAME)
    print("Старий ендпоінт видалено.")
except:
    pass

try:
    sm_client.delete_endpoint_config(EndpointConfigName=ENDPOINT_NAME)
    print(f"  - Old endpoint configuration deleted.")
except:
    pass

huggingface_model = HuggingFaceModel(
    model_data=MODEL_DATA_URL,
    role=ROLE,
    transformers_version='4.51.3',
    pytorch_version='2.6.0',
    py_version='py312',
    entry_point='inference.py', 
    source_dir='app',
    sagemaker_session=sagemaker_session,
    name=f"hybrid-model-{datetime.now().strftime('%H-%M-%S')}"
)

print("Деплой нового ендпоінту (це займе 5-10 хвилин)...")
predictor = huggingface_model.deploy(
    initial_instance_count=1,
    instance_type='ml.m5.xlarge',
    endpoint_name=ENDPOINT_NAME
)

print(f"Готово! Ендпоінт {ENDPOINT_NAME} активний.")

