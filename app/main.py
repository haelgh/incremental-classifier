from fastapi import FastAPI
from pydantic import BaseModel
import boto3
import os
from dotenv import load_dotenv

app = FastAPI()
load_dotenv()

CLASS_NAMES = {
    0: 'alt.atheism', 1: 'comp.graphics', 2: 'comp.os.ms-windows.misc',
    3: 'comp.sys.ibm.pc.hardware', 4: 'comp.sys.mac.hardware', 5: 'comp.windows.x',
    6: 'misc.forsale', 7: 'rec.autos', 8: 'rec.motorcycles',
    9: 'rec.sport.baseball', 10: 'rec.sport.hockey', 11: 'sci.crypt',
    12: 'sci.electronics', 13: 'sci.med', 14: 'sci.space',
    15: 'soc.religion.christian', 16: 'talk.politics.guns',
    17: 'talk.politics.mideast', 18: 'talk.politics.misc', 19: 'talk.religion.misc'
}

runtime = boto3.client('sagemaker-runtime', region_name=os.getenv("AWS_REGION"))

class NewsInput(BaseModel):
    text: str

@app.post("/predict")
def predict(input_data: NewsInput):
    try:
        response = runtime.invoke_endpoint(
            EndpointName=os.getenv("SAGEMAKER_ENDPOINT_NAME"),
            ContentType='text/csv',
            Body=input_data.text
        )
        
        result_str = response['Body'].read().decode('utf-8').strip()
        
        import re
        clean_result = re.sub(r'[\[\]"]', '', result_str)
        pred_index = int(float(clean_result))
        
        category = CLASS_NAMES.get(pred_index, "Unknown")
        
        return {
            "prediction_code": pred_index,
            "category_name": category,
            "status": "success"
        }
    except Exception as e:
        return {"error": str(e), "status": "failed"}