from sklearn.datasets import fetch_20newsgroups
import pandas as pd
import boto3
import os
from dotenv import load_dotenv

load_dotenv() 

def fetch_and_upload_data():
    print("Downloading 20 Newsgroups dataset...")
    newsgroups = fetch_20newsgroups(subset='all', remove=('headers', 'footers', 'quotes'))
    
    print(f"Categories found: {len(newsgroups.target_names)}")

    print(f"Categories list: {newsgroups.target_names}")

    df = pd.DataFrame({'text': newsgroups.data, 'label': newsgroups.target})

    initial_len = len(df)
    df = df[df['text'].str.strip() != ""] 
    print(f"Cleaned empty rows: {initial_len - len(df)} removed.")
    
    local_path = "dataset.csv"
    df.to_csv(local_path, index=False)
    print(f"Saved locally to {local_path}")
    
    bucket_name = os.getenv('S3_BUCKET_NAME')
    region = os.getenv('AWS_REGION', 'eu-north-1')

    s3 = boto3.client('s3', region_name=region)
    
    print(f"Uploading to S3 bucket: {bucket_name}...")
    s3.upload_file(local_path, bucket_name, "data/dataset.csv") 
    print(f"Data successfully uploaded to S3: s3://{bucket_name}/data/dataset.csv")

if __name__ == "__main__":
    fetch_and_upload_data()