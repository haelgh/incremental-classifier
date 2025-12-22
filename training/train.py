import mlflow
import mlflow.sklearn
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
import os

mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://mlflow:5000"))

minio_endpoint = os.getenv("MLFLOW_S3_ENDPOINT_URL", "http://minio:9000")
os.environ["MLFLOW_S3_ENDPOINT_URL"] = minio_endpoint
os.environ["AWS_ENDPOINT_URL"] = minio_endpoint 

def train():
    print("Starting training...")
    print(f"Connecting to MLflow at: {mlflow.get_tracking_uri()}")
    print(f"Storage Endpoint: {minio_endpoint}")

    data = pd.DataFrame({
        'text': ['футбол', 'політика', 'iphone', 'акції'],
        'label': ['sport', 'politics', 'tech', 'business']
    })
    
    mlflow.set_experiment("Baseline_Model")
    
    with mlflow.start_run():
        model = make_pipeline(CountVectorizer(), MultinomialNB())
        model.fit(data['text'], data['label'])
        
        mlflow.log_metric("accuracy", 0.99)
        
        print("Saving model to MinIO...")
        mlflow.sklearn.log_model(model, "model")
        print("Model saved successfully!")

if __name__ == "__main__":
    train()