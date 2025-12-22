from fastapi import FastAPI
from pydantic import BaseModel
from contextlib import asynccontextmanager
import mlflow.sklearn
import os

model = None

os.environ["MLFLOW_S3_ENDPOINT_URL"] = "http://minio:9000"
mlflow.set_tracking_uri("http://mlflow:5000")

@asynccontextmanager
async def lifespan(app: FastAPI):

    global model
    try:

        print("Model loaded successfully (simulation)")
    except Exception as e:
        print(f"Model loading failed: {e}")
    
    yield 
    
    print("Shutting down application...")
    model = None

app = FastAPI(lifespan=lifespan)

class TextRequest(BaseModel):
    text: str

@app.post("/predict")
def predict(request: TextRequest):

    return {
        "text": request.text, 
        "prediction": "sport", 
        "confidence": 0.95,
        "status": "model_loaded" if model else "mock_response"
    }