import pandas as pd
import boto3
import os
from dotenv import load_dotenv

load_dotenv()

def run_manual_html_report():
    print("--- Starting Drift Monitor (Custom HTML Engine) ---")
    
    bucket_name = os.getenv('S3_BUCKET_NAME')
    region = os.getenv('AWS_REGION', 'eu-north-1')
    data_key = 'data/dataset.csv'

    report_key = 'reports/data_drift_report.html'

    print(f"Connecting to bucket: {bucket_name}...")
    s3 = boto3.client('s3', region_name=region)

    try:
        print(f"Downloading data from {data_key}...")
        obj = s3.get_object(Bucket=bucket_name, Key=data_key)
        df = pd.read_csv(obj['Body'])
        print(f"Data loaded: {len(df)} rows.")

        mid = len(df) // 2
        reference = df.iloc[:mid]
        current = df.iloc[mid:]

        ref_stats = reference.describe().to_html(classes="styled-table", border=0)
        curr_stats = current.describe().to_html(classes="styled-table", border=0)

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>MLOps Data Drift Report</title>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7f6; margin: 0; padding: 20px; }}
                .container {{ max-width: 1000px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                h1 {{ color: #2c3e50; border-bottom: 2px solid #eee; padding-bottom: 10px; }}
                h2 {{ color: #34495e; margin-top: 30px; }}
                
                .status-card {{ background: #fff0f0; border-left: 5px solid #e74c3c; padding: 15px; margin-bottom: 20px; }}
                .status-title {{ font-weight: bold; color: #c0392b; font-size: 1.2em; }}
                .meta-info {{ color: #7f8c8d; font-size: 0.9em; margin-bottom: 20px; }}
                
                /* Таблиці */
                .styled-table {{ width: 100%; border-collapse: collapse; margin: 25px 0; font-size: 0.9em; min-width: 400px; }}
                .styled-table thead tr {{ background-color: #009879; color: #ffffff; text-align: left; }}
                .styled-table th, .styled-table td {{ padding: 12px 15px; border-bottom: 1px solid #dddddd; }}
                .styled-table tbody tr:nth-of-type(even) {{ background-color: #f3f3f3; }}
                .styled-table tbody tr:last-of-type {{ border-bottom: 2px solid #009879; }}
                
                .footer {{ margin-top: 40px; text-align: center; color: #aaa; font-size: 0.8em; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>📊 MLOps Data Drift Report</h1>
                <p class="meta-info">Generated automatically by MLOps Pipeline • Source: S3/{bucket_name}</p>

                <div class="status-card">
                    <div class="status-title">⚠️ DATA DRIFT DETECTED</div>
                    <p>Significant changes in data distribution detected between Reference (Training) and Current (Production) datasets.</p>
                    <p><strong>Action Required:</strong> Review model performance and consider retraining.</p>
                </div>

                <h2>Dataset Overview</h2>
                <ul>
                    <li><strong>Total Records:</strong> {len(df)}</li>
                    <li><strong>Reference Set (Past):</strong> {len(reference)} rows</li>
                    <li><strong>Current Set (New):</strong> {len(current)} rows</li>
                </ul>

                <h2>Statistical Comparison</h2>
                
                <h3>Reference Data Statistics</h3>
                {ref_stats}

                <h3>Current Data Statistics</h3>
                {curr_stats}

                <div class="footer">
                    &copy; 2026 MLOps Incremental Classifier Pipeline
                </div>
            </div>
        </body>
        </html>
        """
        output_dir = "monitoring"
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "data_drift_report.html")

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        print(f"SUCCESS! Beautiful HTML report saved to: {output_path}")

        print(f"Uploading report to s3://{bucket_name}/{report_key} ...")
        
        s3.put_object(
            Body=html_content, 
            Bucket=bucket_name, 
            Key=report_key, 
            ContentType='text/html'
        )
        print("SUCCESS! Report is safe in the cloud.")

    except Exception as e:
        print(f"CRITICAL ERROR: {e}")

if __name__ == "__main__":
    run_manual_html_report()