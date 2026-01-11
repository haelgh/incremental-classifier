import boto3
import os
from dotenv import load_dotenv

load_dotenv()

BUCKET_NAME = os.getenv('S3_BUCKET_NAME')
LOCAL_FILE = 'dataset.csv'
S3_KEY = 'data/dataset.csv'

s3 = boto3.client('s3', region_name='eu-north-1')

def upload():
    print(f"Uploading {LOCAL_FILE} to s3://{BUCKET_NAME}/{S3_KEY} ...")
    
    if not os.path.exists(LOCAL_FILE):
        print(f"ERROR: Local file {LOCAL_FILE} not found! Put your CSV there.")
        return

    try:
        s3.upload_file(LOCAL_FILE, BUCKET_NAME, S3_KEY)
        print("Success! Data is now in S3.")
    except Exception as e:
        print(f"Upload failed: {e}")

if __name__ == "__main__":
    upload()