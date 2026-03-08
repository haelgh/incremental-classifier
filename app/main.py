from fastapi import FastAPI
from pydantic import BaseModel
import boto3
import os
from dotenv import load_dotenv
import json

app = FastAPI()
load_dotenv()

CLASS_NAMES = {
    0: "World/Politics",
    1: "Sports",
    2: "Business/Finance",
    3: "Tech/Science",
    4: "Anger/Complaint",
    5: "Joy/Appreciation",
    6: "Optimism/Proposal",
    7: "Sadness/Crisis"
}
runtime = boto3.client('sagemaker-runtime', region_name=os.getenv("AWS_REGION", "eu-north-1"))

class NewsInput(BaseModel):
    text: str

@app.post("/predict")
def predict(input_data: NewsInput):
    try:
        payload = json.dumps({"text": input_data.text})
        
        response = runtime.invoke_endpoint(
            EndpointName=os.getenv("SAGEMAKER_ENDPOINT_NAME", "news-classifier-endpoint"),
            ContentType='application/json',
            Body=payload
        )
        
        result_str = response['Body'].read().decode('utf-8').strip()
        
        import re
        clean_result = re.sub(r'[\[\]"]', '', result_str)
        pred_index = int(float(clean_result))
        
        category = CLASS_NAMES.get(pred_index, "Unknown")
        
        return {
            "predicted_class_id": pred_index,
            "predicted_label": category,
            "status": "success"
        }
    except Exception as e:
        return {"error": str(e), "status": "failed"}