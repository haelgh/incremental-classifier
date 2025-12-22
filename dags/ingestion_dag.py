from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import boto3
import pandas as pd
from io import StringIO
import os

def upload_data():

    s3 = boto3.client('s3',
                      endpoint_url='http://minio:9000',
                    
                      aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                      aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'))
    
    bucket_name = 'news-data'
    try:
        s3.create_bucket(Bucket=bucket_name)
    except:
        pass

    data = pd.DataFrame({
        'text': ['news 1', 'news 2', 'news 3'],
        'label': ['sport', 'politics', 'tech']
    })
    
    csv_buffer = StringIO()
    data.to_csv(csv_buffer, index=False)
    s3.put_object(Bucket=bucket_name, Body=csv_buffer.getvalue(), Key='dataset.csv')
    print("Data uploaded to MinIO")

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
}

with DAG('data_ingestion', default_args=default_args, schedule_interval='@daily', catchup=False) as dag:
    task = PythonOperator(
        task_id='upload_to_minio',
        python_callable=upload_data
    )