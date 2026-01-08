import os
import joblib
import json
import time
import boto3

cloudwatch = boto3.client('cloudwatch')

def model_fn(model_dir):
    model_path = os.path.join(model_dir, "model.joblib")
    return joblib.load(model_path)

def input_fn(request_body, content_type):
    if content_type == 'application/json':
        request = json.loads(request_body)
        return request.get('text', [])
    return [request_body]

def predict_fn(input_data, model):

    start_time = time.time()
    
    prediction = model.predict(input_data)
    
    latency = (time.time() - start_time) * 1000
    
    try:
        cloudwatch.put_metric_data(
            Namespace='IncrementalNewsClassifier',
            MetricData=[{
                'MetricName': 'InferenceLatency',
                'Value': latency,
                'Unit': 'Milliseconds'
                
            }]
        )
    except Exception as e:
        print(f"CloudWatch metrics failed: {e}")
        
    return prediction

def output_fn(prediction, content_type):
    return json.dumps(prediction.tolist())