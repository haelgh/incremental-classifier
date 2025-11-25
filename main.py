from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Classifier")

class TextRequest(BaseModel):
    text: str

# Main page
@app.get("/")
def read_root():
    return {"message": "Hi! The system is working"}

#Predict func}
@app.post("/predict")
def predict(request: TextRequest):
    # Place for model, return test answer
    return {
        "input_text": request.text,
        "prediction": "Технології",  # Example category
        "confidence": 0.99
    }