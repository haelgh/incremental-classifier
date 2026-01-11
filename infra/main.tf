terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "eu-north-1"
  ignore_tags {
    key_prefixes = ["aws:"]
  }
}

resource "aws_s3_bucket" "mlops_bucket" {
  bucket = "incremental-classifier-storage-final-prod"
  
  tags = {
    Name = "MLOps Lab4 Storage"
    Environment = "Production"
  }
}

resource "aws_s3_bucket_versioning" "versioning" {
  bucket = aws_s3_bucket.mlops_bucket.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_sns_topic" "alerts" {
  name = "mlops-drift-alerts"
}

resource "aws_sns_topic_subscription" "email_alert" {
  topic_arn = aws_sns_topic.alerts.arn
  protocol = "email"
  endpoint  = "tytarenko.olha@lll.kpi.ua"
}

resource "aws_cloudwatch_metric_alarm" "model_error_alarm" {
  alarm_name          = "HighModelErrors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "ModelErrors"
  namespace           = "NewsClassifier"
  period              = "300"
  statistic           = "Sum"
  threshold           = "1"
  alarm_description   = "Trigger this alarm if model errors spike"
  actions_enabled     = true
  alarm_actions       = [aws_sns_topic.alerts.arn]
}

output "bucket_name" {
  value = aws_s3_bucket.mlops_bucket.bucket
}

output "sns_topic_arn" {
  value = aws_sns_topic.alerts.arn
}