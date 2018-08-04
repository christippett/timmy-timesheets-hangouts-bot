terraform {
    required_version        = ">=0.11.7"

    backend "s3" {
        bucket              = "team2-terralock"
        key                 = "Team2/terraform/global/iam/terraform.tfstate"
        region              = "ap-southeast-2"
        encrypt             = "true"
        dynamodb_table      = "team2-terralocker"
    }
}

provider "aws" {
    region = "ap-southeast-2"
    profile = "team2servian"
}


# DELETED FROM KMS block - 2 missing

# "${data.terraform_remote_state.dynamodb.dynamodb_team2_user_register_kms_key_arn}",
# "${data.terraform_remote_state.sqs.sqs_kms_key_arn}",
# "${data.terraform_remote_state.sqs.sqs_ssm_kms_key_arn}",
# "${data.terraform_remote_state.kms.s3_kms_key_arn}",
# "${data.terraform_remote_state.s3.s3_ssm_kms_key_arn}",
# "${data.terraform_remote_state.ssm.google_auth_client_secret_kms_key_arn}",
# "${data.terraform_remote_state.ssm.google_auth_service_account_kms_key_arn}"

resource "aws_iam_role" "timesheets_lambda" {
    name = "team2-timesheets-lambda-role"
    force_detach_policies = true

    assume_role_policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": "sts:AssumeRole",
            "Principal": {
                "Service": "lambda.amazonaws.com",
                "AWS": ["arn:aws:iam::204449496694:user/team2"]
            },
            "Effect": "Allow",
            "Sid": "LambdaAssumeRole"
        }
    ]
}
EOF
}

resource "aws_iam_policy" "timesheets_lambda" {
  name        = "team2-timesheets-lambda-policy"
  path        = "/"
  description = "Team 2 Chalice lambda policy"

  policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "arn:aws:logs:*:*:*"
        },
        {
            "Effect":"Allow",
            "Action":[
                "kms:Encrypt",
                "kms:Decrypt"
            ],
            "Resource": [
                "*"
            ]
        },
        {
            "Effect":"Allow",
            "Action":[
                "sqs:DeleteMessage",
                "sqs:GetQueueAttributes",
                "sqs:GetQueueUrl",
                "sqs:SendMessage",
                "sqs:ReceiveMessage",
                "sqs:PurgeQueue"
            ],
            "Resource":"${data.terraform_remote_state.sqs.sqs_arn}"
        },
        {
            "Effect":"Allow",
            "Action":[
                "ssm:*"
            ],
            "Resource": [
                "arn:aws:ssm:${data.terraform_remote_state.shared.region}:${data.terraform_remote_state.shared.account_id}:parameter/team2*"
            ]
        },
        {
            "Effect":"Allow",
            "Action":[
                "dynamodb:BatchGetItem",
                "dynamodb:BatchWriteItem",
                "dynamodb:DeleteItem",
                "dynamodb:DescribeTable",
                "dynamodb:DescribeTimeToLive",
                "dynamodb:GetItem",
                "dynamodb:GetRecords",
                "dynamodb:PutItem",
                "dynamodb:Query",
                "dynamodb:Scan",
                "dynamodb:UpdateItem"
            ],
            "Resource": [
                "${data.terraform_remote_state.dynamodb.dynamodb_team2_user_arn}",
                "${data.terraform_remote_state.dynamodb.dynamodb_team2_user_register_arn}",
                "${data.terraform_remote_state.dynamodb.dynamodb_team2_space_arn}"
            ]
        },
        {
            "Sid":"AuthorizeAccount",
            "Effect":"Allow",
            "Resource":"${data.terraform_remote_state.ses.ses_identity_arn}",
            "Action":[
                "SES:SendEmail",
                "SES:SendRawEmail"
            ]
        }
    ]
}
EOF
}

resource "aws_iam_policy_attachment" "timesheets_lambda" {
  name       = "team2-timesheets-attach-policy"
  roles      = ["${aws_iam_role.timesheets_lambda.name}"]
  policy_arn = "${aws_iam_policy.timesheets_lambda.arn}"
}

module "ssm_iam" {
    source                      = "../../modules/ssm"
    service_name                = "team2-kms-iam"
    qualified_path_to_outputs   = "/team2/global/iam/iam_terraform_outputs"
    terraform_outputs           = "${map("team2-timesheets-lambda-role-arn", aws_iam_role.timesheets_lambda.arn)}"
    global_tags                 = "${data.terraform_remote_state.shared.global_tags}"
}

