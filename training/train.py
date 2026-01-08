import argparse
import os
import json
import pandas as pd
import joblib
import boto3
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.metrics import f1_score
from sklearn.model_selection import train_test_split
import mlflow

def get_production_metric(group_name):
    try:
        client = boto3.client('sagemaker', region_name='eu-north-1')
        response = client.list_model_packages(
            ModelPackageGroupName=group_name,
            ModelApprovalStatus='Approved',
            SortBy='CreationTime',
            SortOrder='Descending'
        )

        if response['ModelPackageSummaryList']:
            return 0.60
        return 0.0
    except Exception as e:
        print(f"Warning: Could not check registry ({e}). Using default threshold 0,6.")
        return 0.6

def train(train_path, model_dir, group_name):
    print(f"Reading data from: {train_path}")
    
    data_file = os.path.join(train_path, 'dataset.csv')
    df = pd.read_csv(data_file)
    
    X_train, X_test, y_train, y_test = train_test_split(df['text'], df['label'], test_size=0.2, random_state=42)

    mlflow.set_experiment("News_Classifier_Lab3")
    with mlflow.start_run():
    
        base_pipe = Pipeline([
            ('tfidf', TfidfVectorizer(max_features=5000)), 
            ('clf', MultinomialNB())
        ])
        base_pipe.fit(X_train, y_train)
        f1_base = f1_score(y_test, base_pipe.predict(X_test), average='macro')
        print(f"Baseline F1: {f1_base}")
        mlflow.log_metric("baseline_f1", f1_base)

        imp_pipe = Pipeline([
            ('tfidf', TfidfVectorizer(max_features=5000)), 
            ('clf', RandomForestClassifier(n_estimators=50, random_state=42))
        ])
        imp_pipe.fit(X_train, y_train)
        f1_imp = f1_score(y_test, imp_pipe.predict(X_test), average='macro')
        print(f"Improved F1: {f1_imp}")
        mlflow.log_metric("improved_f1", f1_imp)

        if f1_imp >= f1_base:
            best_model = imp_pipe
            best_f1 = f1_imp
        else:
            best_model = base_pipe
            best_f1 = f1_base

        prod_metric = get_production_metric(group_name)
        print(f"New F1: {best_f1:.4f}, Prod Threshold: {prod_metric}")

        report_dict = {
            "classification_metrics": {
                "f1": { 
                    "value": float(best_f1)
                }
            }
        }
        evaluation_path = os.path.join(model_dir, "evaluation.json") 
        with open(evaluation_path, "w") as f:
            json.dump(report_dict, f)

        print(f"Evaluation report saved to {evaluation_path}")

        joblib.dump(best_model, os.path.join(model_dir, "model.joblib"))
        
        if best_f1 > prod_metric:
            print("Status: quality gate passed.")
        else:
            print("Status: quality gate warning (lower than prod).")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    
    parser.add_argument('--model-dir', type=str, default=os.environ.get('SM_MODEL_DIR'))
    parser.add_argument('--train', type=str, default=os.environ.get('SM_CHANNEL_TRAIN'))
    parser.add_argument('--group-name', type=str, default="NewsClassificationGroup")
    
    args = parser.parse_args()
    train(args.train, args.model_dir, args.group_name)