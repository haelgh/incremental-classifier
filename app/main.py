from fastapi import FastAPI
from pydantic import BaseModel
import boto3
import os
from dotenv import load_dotenv

app = FastAPI()
load_dotenv()

CLASS_NAMES = {
    0: 'Клас 0 (Офіційні новини / Негатив)',
    1: 'Клас 1 (Спорт / Позитив)',
    2: 'Клас 2 (Бізнес / Нейтрально)',
    3: 'Клас 3 (Технології / Емоції)'
}

runtime = boto3.client('sagemaker-runtime', region_name=os.getenv("AWS_REGION", "eu-north-1"))

class NewsInput(BaseModel):
    text: str

@app.post("/predict")
def predict(input_data: NewsInput):
    try:
        response = runtime.invoke_endpoint(
            EndpointName=os.getenv("SAGEMAKER_ENDPOINT_NAME", "continual-learning-endpoint"),
            ContentType='application/json',
            Body='{"text": "' + input_data.text.replace('"', '\\"') + '"}'
        )
        
        result = response['Body'].read().decode('utf-8')
        class_id = int(result.strip('[]'))
        
        return {
            "predicted_class_id": class_id,
            "predicted_label": CLASS_NAMES.get(class_id, "Невідомий клас")
        }
    except Exception as e:
        return {"error": str(e)}