import boto3
import pandas as pd
from io import StringIO
import os
from sklearn.datasets import fetch_20newsgroups
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

BUCKET_NAME = os.getenv('S3_BUCKET_NAME', 'incremental-classifier-storage')
PIPELINE_NAME = 'NewsClassificationPipeline'
REGION = os.getenv('AWS_REGION', 'eu-north-1')

def upload_real_data_to_s3():
    s3 = boto3.client('s3', region_name=REGION)
    
    local_file_path = '/opt/airflow/dags/dataset.csv'
    
    if os.path.exists(local_file_path):
        print(f"Loading local file {local_file_path}...")
        with open(local_file_path, "rb") as f:
            s3.upload_fileobj(f, BUCKET_NAME, 'data/dataset.csv')
        print(f"Successfully uploaded to s3://{BUCKET_NAME}/data/dataset.csv")
    else:
        print(f"Error: file NOT found at {local_file_path}")
        print(f"Current directory: {os.getcwd()}")
        raise FileNotFoundError(f"Missing {local_file_path}")

def trigger_sagemaker_pipeline():
    sm_client = boto3.client('sagemaker', region_name=REGION)
    response = sm_client.start_pipeline_execution(
        PipelineName=PIPELINE_NAME,
        PipelineExecutionDescription=f"Run_triggered_by_Airflow_{datetime.now().strftime('%Y%m%d')}"
    )
    print(f"SageMaker Pipeline execution started: {response['PipelineExecutionArn']}")

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 1, 1),
    'retries': 1,
}

with DAG('news_mlops_pipeline', default_args=default_args, schedule_interval='@daily', catchup=False) as dag:
    
    fetch_data_task = PythonOperator(
        task_id='upload_to_s3',
        python_callable=upload_real_data_to_s3
    )

    trigger_pipeline_task = PythonOperator(
        task_id='trigger_sagemaker_pipeline',
        python_callable=trigger_sagemaker_pipeline
    )

    fetch_data_task >> trigger_pipeline_task