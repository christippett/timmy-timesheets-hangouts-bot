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
                "kms:Decrypt",
                "kms:GenerateDataKey"
            ],
            "Resource": [
                "${data.terraform_remote_state.dynamodb.dynamodb_team2_user_register_kms_key_arn}",
                "${data.terraform_remote_state.sqs.sqs_chat_kms_key_arn}",
                "${data.terraform_remote_state.sqs.sqs_scrape_kms_key_arn}",
                "${data.terraform_remote_state.sqs.sqs_process_kms_key_arn}",
                "${data.terraform_remote_state.sqs.sqs_ssm_kms_key_arn}",
                "${data.terraform_remote_state.kms.s3_kms_key_arn}",
                "${data.terraform_remote_state.kms.ssm_kms_key_arn}",
                "${data.terraform_remote_state.s3.s3_ssm_kms_key_arn}",
                "${data.terraform_remote_state.ssm.google_auth_client_secret_kms_key_arn}",
                "${data.terraform_remote_state.ssm.google_auth_service_account_kms_key_arn}",
                "${data.terraform_remote_state.ssm.oauth_cipher_kms_key_arn}",
                "${data.terraform_remote_state.ses.ses_ssm_kms_key_arn}",
                "${data.terraform_remote_state.acm.acm_kms_key_arn}"
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
            "Resource":[
                "${data.terraform_remote_state.sqs.sqs_scrape_arn}",
                "${data.terraform_remote_state.sqs.sqs_chat_arn}",
                "${data.terraform_remote_state.sqs.sqs_process_arn}"
            ]
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
                "${data.terraform_remote_state.dynamodb.dynamodb_team2_space_arn}",
                "${data.terraform_remote_state.dynamodb.dynamodb_team2_timesheets_arn}"
            ]
        },
        {
            "Sid":"AuthorizeAccount",
            "Effect":"Allow",
            "Resource":"*",
            "Action":[
                "SES:SendEmail",
                "SES:SendRawEmail",
                "SES:SendCustomVerificationEmail"
            ],
            "Condition":{
                "ForAllValues:StringLike":{
                    "ses:Recipients":[
                        "*@servian.com",
                        "*@servian.com.au"
                    ]
                }
            }
        },
        {
            "Effect":"Allow",
            "Resource":"*",
            "Action":[
                "SES:CreateCustomVerificationEmailTemplate",
                "SES:DeleteCustomVerificationEmailTemplate",
                "SES:DeleteVerifiedEmailAddress",
                "SES:GetCustomVerificationEmailTemplate",
                "SES:ListCustomVerificationEmailTemplates",
                "SES:ListVerifiedEmailAddresses",
                "SES:UpdateCustomVerificationEmailTemplate"
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
