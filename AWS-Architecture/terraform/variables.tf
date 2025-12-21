variable "region" {
  default = "ca-central-1"
}


variable "ecr_image" {
  description = "ECR image for ECS"
  default = "106571671946.dkr.ecr.ca-central-1.amazonaws.com/fraud-detection-repo:latest"
}

variable "rds_username" {}
variable "rds_password" {}

variable "redshift_username" {}
variable "redshift_password" {}


variable "grafana_redshift_policy_json" {
  type    = string
  default = <<EOT
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowReadingMetricsFromRedshift",
      "Effect": "Allow",
      "Action": [
        "redshift-data:ListTables",
        "redshift-data:DescribeTable",
        "redshift-data:GetStatementResult",
        "redshift-data:DescribeStatement",
        "redshift-data:ListStatements",
        "redshift-data:ListSchemas",
        "redshift-data:ExecuteStatement",
        "redshift-data:CancelStatement",
        "redshift:GetClusterCredentials",
        "redshift:DescribeClusters",
        "redshift-serverless:ListWorkgroups",
        "redshift-serverless:GetCredentials",
        "secretsmanager:ListSecrets"
      ],
      "Resource": "*"
    },
    {
      "Sid": "AllowReadingRedshiftQuerySecrets",
      "Effect": "Allow",
      "Action": ["secretsmanager:GetSecretValue"],
      "Resource": "*",
      "Condition": {
        "Null": {
          "secretsmanager:ResourceTag/RedshiftQueryOwner": "false"
        }
      }
    }
  ]
}
EOT
}

