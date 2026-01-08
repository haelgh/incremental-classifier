import os
import boto3
import sagemaker
from sagemaker.sklearn.processing import SKLearnProcessor
from sagemaker.processing import ProcessingInput, ProcessingOutput
from sagemaker.workflow.steps import ProcessingStep, TrainingStep, CreateModelStep
from sagemaker.workflow.condition_step import ConditionStep
from sagemaker.workflow.pipeline_context import PipelineSession
from sagemaker.workflow.conditions import ConditionGreaterThanOrEqualTo
from sagemaker.workflow.functions import JsonGet
from sagemaker.workflow.pipeline import Pipeline
from sagemaker.sklearn.estimator import SKLearn
from sagemaker.sklearn.model import SKLearnModel
from sagemaker.workflow.step_collections import RegisterModel
from sagemaker.workflow.properties import PropertyFile
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(dotenv_path)

role = os.getenv('AWS_ROLE_ARN')
bucket_name = os.getenv('S3_BUCKET_NAME')
region = os.getenv('AWS_REGION', 'eu-north-1')
MLFLOW_TRACKING_URI = os.getenv('MLFLOW_TRACKING_URI')

boto_session = boto3.Session(region_name=region)
sagemaker_session = PipelineSession(boto_session=boto_session)

evaluation_report = PropertyFile(
    name="EvaluationReport",
    output_name="evaluation",
    path="evaluation.json"
)

drift_processor = SKLearnProcessor(
    framework_version="1.0-1",
    instance_type="ml.m5.large",
    instance_count=1,
    base_job_name="data-drift-check",
    role=role,
    sagemaker_session=sagemaker_session
)

step_drift = ProcessingStep(
    name="DataDriftAnalysis",
    processor=drift_processor,
    inputs=[ProcessingInput(source=f"s3://{bucket_name}/data/dataset.csv", destination="/opt/ml/processing/input")],
    outputs=[ProcessingOutput(output_name="drift_report", source="/opt/ml/processing/output", destination=f"s3://{bucket_name}/monitoring/reports")],
    code="monitoring/monitor_drift.py"
)

sklearn_estimator = SKLearn(
    entry_point='train.py',
    source_dir='training',
    role=role,
    instance_type='ml.m5.large',
    py_version='py3',
    framework_version='1.0-1',
    sagemaker_session=sagemaker_session,
    base_job_name="news-training-job",
    output_path=f"s3://{bucket_name}/training_output",
    environment={
        "MLFLOW_TRACKING_URI": MLFLOW_TRACKING_URI,
        "MLFLOW_EXPERIMENT_NAME": "News_Classifier_Lab3"
    }
)

step_train = TrainingStep(
    name="TrainNewsModel",
    estimator=sklearn_estimator,
    inputs={"train": sagemaker.inputs.TrainingInput(s3_data=f"s3://{bucket_name}/data/dataset.csv", content_type="text/csv")}
)

step_eval = ProcessingStep(
    name="EvaluateNewsModel", 
    processor=drift_processor,
    inputs=[
        ProcessingInput(
            source=step_train.properties.ModelArtifacts.S3ModelArtifacts,
            destination="/opt/ml/processing/model"
        )
    ],
    outputs=[ProcessingOutput(output_name="evaluation", source="/opt/ml/processing/output")],
    property_files=[evaluation_report],
    code="training/evaluate.py"
)

model = SKLearnModel(
    entry_point='inference.py',
    source_dir='app',
    role=role,
    sagemaker_session=sagemaker_session,
    framework_version='1.0-1',
    model_data=step_train.properties.ModelArtifacts.S3ModelArtifacts
)

step_create_model = CreateModelStep(
    name="CreateNewsModel",
    model=model,
    inputs=sagemaker.inputs.CreateModelInput(instance_type="ml.m5.large")
)

step_register = RegisterModel(
    name="RegisterNewsModel",
    estimator=sklearn_estimator,
    model_data=step_train.properties.ModelArtifacts.S3ModelArtifacts,
    content_types=["text/csv"],
    response_types=["text/csv"],
    inference_instances=["ml.m5.large"],
    transform_instances=["ml.m5.large"],
    model_package_group_name="NewsClassificationGroup",
    approval_status="Approved",
)

step_deploy = ProcessingStep(
    name="DeployNewsModel",
    processor=drift_processor,
    code="pipeline_definitions/deploy_model.py",
    job_arguments=[
        "--model_data_url", step_train.properties.ModelArtifacts.S3ModelArtifacts,
        "--region", region,
        "--role", role
    ]
)

cond_gte = ConditionGreaterThanOrEqualTo(
    left=JsonGet(
        step_name=step_eval.name,
        property_file=evaluation_report,
        json_path="classification_metrics.f1.value"
    ),
    right=0.6
)

step_cond = ConditionStep(
    name="CheckF1Threshold",
    conditions=[cond_gte],
    if_steps=[step_create_model, step_register, step_deploy],
    else_steps=[]
)

pipeline = Pipeline(
    name="NewsClassificationPipeline",
    steps=[step_drift, step_train, step_eval, step_cond], 
    sagemaker_session=sagemaker_session
)

pipeline.upsert(role_arn=role)
print("SageMaker Pipeline with Auto-Deploy registered successfully!")