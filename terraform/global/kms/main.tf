terraform {
    required_version        = ">=0.11.7"

    backend "s3" {
        bucket              = "team2-terralock"
        key                 = "Team2/terraform/global/kms/terraform.tfstate"
        region              = "ap-southeast-2"
        encrypt             = "true"
        dynamodb_table      = "team2-terralocker"
    }
}

provider "aws" {
    region = "ap-southeast-2"
    profile = "team2servian"
}

# TODO: All individual keys created here in separate tf files
# unless they can be linked to the module for the relevant
# service

module "kms-s3-app" {
    source          = "../../modules/kms"
    service_name    = "team2-app-kms-S3"
    global_tags     = "${data.terraform_remote_state.shared.global_tags}"
}

module "ssm_kms_kms" {
    source                      = "../../modules/ssm"
    service_name                = "team2-kms-S3"
    qualified_path_to_outputs   = "/team2/global/kms/kms_terraform_outputs"
    terraform_outputs           = "${map("kms-s3-app-arn", module.kms-s3-app.kms_key_arn, "kms-s3-app-id", module.kms-s3-app.kms_key_id)}"
    global_tags                 = "${data.terraform_remote_state.shared.global_tags}"
}
