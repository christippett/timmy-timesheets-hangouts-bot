terraform {
    required_version        = ">=0.11.7"

    backend "s3" {
        bucket              = "team2-terralock"
        key                 = "Team2/terraform/service/sqs/terraform.tfstate"
        region              = "ap-southeast-2"
        encrypt             = "true"
        dynamodb_table      = "team2-terralocker"
    }
}

provider "aws" {
    region  = "ap-southeast-2"
    profile = "team2servian"
}

module "kms_sqs_chat" {
    source          = "../../modules/kms"
    service_name    = "team2-kms-sqs-chat"
    global_tags     = "${data.terraform_remote_state.shared.global_tags}"
}

module "kms_sqs_scrape" {
    source          = "../../modules/kms"
    service_name    = "team2-kms-sqs-scrape"
    global_tags     = "${data.terraform_remote_state.shared.global_tags}"
}

resource "aws_sqs_queue" "sqs_queue_chat" {
    name                                = "team2-sqs-chat"
    kms_master_key_id                   = "${module.kms_sqs_chat.kms_key_id}"
    kms_data_key_reuse_period_seconds   = 300
    # Overriding default of 30 as lambda execution timeout is set at 60
    visibility_timeout_seconds          = 120
    tags                                = "${data.terraform_remote_state.shared.global_tags}"
}

resource "aws_sqs_queue" "sqs_queue_scrape" {
    name                                = "team2-sqs-scrape"
    kms_master_key_id                   = "${module.kms_sqs_scrape.kms_key_id}"
    kms_data_key_reuse_period_seconds   = 300
    # Overriding default of 30 as lambda execution timeout is set at 60
    visibility_timeout_seconds          = 120
    tags                                = "${data.terraform_remote_state.shared.global_tags}"
}

module "ssm_sqs" {
    source                      = "../../modules/ssm"
    service_name                = "team2-sqs"
    qualified_path_to_outputs   = "/team2/service/sqs/sqs_terraform_outputs"
    terraform_outputs           = "${map("sqs_chat_kms_arn", module.kms_sqs_chat.kms_key_arn, "sqs_queue_chat_arn", aws_sqs_queue.sqs_queue_chat.arn, "sqs_queue_chat_id", aws_sqs_queue.sqs_queue_chat.id, "sqs_scrape_kms_arn", module.kms_sqs_scrape.kms_key_arn, "sqs_scrape_chat_arn", aws_sqs_queue.sqs_queue_scrape.arn, "sqs_queue_scrape_id", aws_sqs_queue.sqs_queue_scrape.id)}"
    global_tags                 = "${data.terraform_remote_state.shared.global_tags}"
}
