import os
import json
import time
import boto3
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

cloudwatch = boto3.client('cloudwatch')

def model_fn(model_dir, context=None):
    
    actual_model_dir = model_dir
    
    # Якщо в корені немає config.json, шукаємо його у підпапках
    if not os.path.exists(os.path.join(model_dir, 'config.json')):
        print("config.json не знайдено в корені. Перевіряємо підпапки...")
        for item in os.listdir(model_dir):
            item_path = os.path.join(model_dir, item)

            if os.path.isdir(item_path) and os.path.exists(os.path.join(item_path, 'config.json')):
                actual_model_dir = item_path
                break
                
    print(f"Loading model from {actual_model_dir}")
    tokenizer = AutoTokenizer.from_pretrained(actual_model_dir)
    model = AutoModelForSequenceClassification.from_pretrained(actual_model_dir)
    return {'model': model, 'tokenizer': tokenizer}

def input_fn(request_body, request_content_type, context=None):
    if isinstance(request_body, bytes):
        request_body = request_body.decode('utf-8')
        
    if request_content_type == 'application/json':
        request = json.loads(request_body)
        return request.get('text', "")
        
    return request_body

def predict_fn(input_data, model_dict, context=None):
    start_time = time.time()
    
    model = model_dict['model']
    tokenizer = model_dict['tokenizer']

    if not isinstance(input_data, (str, list)):
        input_data = str(input_data)

    inputs = tokenizer(input_data, return_tensors="pt", truncation=True, padding=True, max_length=128)
    
    with torch.no_grad():
        outputs = model(**inputs)
    
    prediction = torch.argmax(outputs.logits, dim=-1).item()
    
    latency = (time.time() - start_time) * 1000
    try:
        cloudwatch.put_metric_data(
            Namespace='ContinualLearningClassifier',
            MetricData=[{'MetricName': 'InferenceLatency', 'Value': latency, 'Unit': 'Milliseconds'}]
        )
    except Exception:
        pass
        
    return [prediction]

def output_fn(prediction, accept, context=None):
    return json.dumps(prediction)