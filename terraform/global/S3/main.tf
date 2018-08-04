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
