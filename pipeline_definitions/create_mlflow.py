import os
import boto3
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(dotenv_path)

role_arn = os.getenv('AWS_ROLE_ARN')
bucket_name = os.getenv('S3_BUCKET_NAME')
region = os.getenv('AWS_REGION', 'eu-north-1')

sm_client = boto3.client('sagemaker', region_name=region)

try:
    response = sm_client.create_mlflow_tracking_server(
        TrackingServerName="news-mlflow-server",
        ArtifactStoreUri=f"s3://{bucket_name}/mlflow/",
        TrackingServerSize="Small",
        RoleArn=role_arn
    )
    print("Request sent successfully!")
    print(f"Tracking Server ARN: {response['TrackingServerArn']}")
except Exception as e:
    print(f"Error: {e}")