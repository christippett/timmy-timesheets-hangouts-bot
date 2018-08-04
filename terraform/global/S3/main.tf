terraform {
    required_version        = ">=0.11.7"

    backend "s3" {
        bucket              = "team2-terralock"
        key                 = "Team2/terraform/global/S3/terraform.tfstate"
        region              = "ap-southeast-2"
        encrypt             = "true"
        dynamodb_table      = "team2-terralocker"
    }
}

provider "aws" {
    region = "ap-southeast-2"
    profile = "team2servian"
}

resource "aws_s3_bucket" "website" {
    bucket                  = "team2-website-servian"
    acl                     = "public-read"
    force_destroy           = "true"
    tags                    = "${data.terraform_remote_state.shared.global_tags}"
    region                  = "${data.terraform_remote_state.shared.region}"

    versioning {
        enabled             = "true"
    }

    website {
        index_document = "index.html"
        error_document = "error.html"
    }
}

resource "aws_s3_bucket_policy" "website" {
    bucket = "${aws_s3_bucket.website.id}"

    policy = <<POLICY
{
    "Version": "2012-10-17",
    "Statement": [
        {

            "Sid": "AllowLambdaToListBucket",
            "Effect": "Allow",
            "Principal": {
                "AWS" : ["${data.terraform_remote_state.iam.timesheets_lambda_role_arn}"]
            },
            "Action": [ 
                "s3:ListBucket"
            ],
            "Resource": "${aws_s3_bucket.website.arn}"
        },
        {
            "Sid":"PublicReadGetObject",
            "Effect":"Allow",
            "Principal": "*",
            "Action":[
                "s3:GetObject"
            ],
            "Resource": "${aws_s3_bucket.website.arn}/*"
        },
        {
            "Sid": "AllowLambdaToUpdateBucket",
            "Effect": "Allow",
            "Principal": {
                "AWS" : ["${data.terraform_remote_state.iam.timesheets_lambda_role_arn}"]
            },
            "Action": [
                "s3:PutObject",
                "s3:DeleteObject"
            ],
            "Resource": "${aws_s3_bucket.website.arn}/*"
        }
    ]
}
POLICY
}


resource "aws_s3_bucket" "app" {
    # TODO: Change name to mapped route53 domain
    bucket                  = "team2-app-servian"
    acl                     = "private"
    force_destroy           = "true"
    tags                    = "${data.terraform_remote_state.shared.global_tags}"
    region                  = "${data.terraform_remote_state.shared.region}"

    versioning {
        enabled             = "true"
    }

    server_side_encryption_configuration {
        rule {
            apply_server_side_encryption_by_default {
                kms_master_key_id = "${data.terraform_remote_state.kms.s3_kms_key_id}"
                sse_algorithm     = "aws:kms"
            }
        }
    }
}

resource "aws_s3_bucket_policy" "app" {
    bucket = "${aws_s3_bucket.app.id}"

    policy = <<POLICY
{
    "Version": "2012-10-17",
    "Statement": [
        {

            "Sid": "AllowLambdaToListBucket",
            "Effect": "Allow",
            "Principal": {
                "AWS" : ["${data.terraform_remote_state.iam.timesheets_lambda_role_arn}"]
            },
            "Action": [ 
                "s3:ListBucket"
            ],
            "Resource": "${aws_s3_bucket.app.arn}"
        },
        {
            "Sid": "AllowLambdaToUpdateBucket",
            "Effect": "Allow",
            "Principal": {
                "AWS" : ["${data.terraform_remote_state.iam.timesheets_lambda_role_arn}"]
            },
            "Action": [
                "s3:PutObject",
                "s3:DeleteObject"
            ],
            "Resource": "${aws_s3_bucket.app.arn}/*"
        }
    ]
}
POLICY
}

module "ssm_kms_s3" {
    source                      = "../../modules/ssm"
    service_name                = "team2-s3"
    qualified_path_to_outputs   = "/team2/global/S3/S3_terraform_outputs"
    terraform_outputs           = "${map("website_endpoint", aws_s3_bucket.website.website_endpoint, "website_bucket_id", aws_s3_bucket.website.id, "app_bucket_id", aws_s3_bucket.app.id, "website_bucket_arn", aws_s3_bucket.website.arn, "app_bucket_arn", aws_s3_bucket.app.arn)}"
    global_tags                 = "${data.terraform_remote_state.shared.global_tags}"
}

