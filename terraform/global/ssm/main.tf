terraform {
    required_version        = ">=0.11.7"

    backend "s3" {
        bucket              = "team2-terralock"
        key                 = "Team2/terraform/global/ssm/terraform.tfstate"
        region              = "ap-southeast-2"
        encrypt             = "true"
        dynamodb_table      = "team2-terralocker"
    }
}

provider "aws" {
    region = "ap-southeast-2"
    profile = "team2servian"
}

module "ssm_google_auth_client_secret" {
    source                      = "../../modules/ssm"
    service_name                = "team2-ssm-google-auth-client-secret"
    qualified_path_to_outputs   = "/team2/global/ssm/google_auth_client_secret"
    terraform_outputs           = "${map("google_auth_client_secret", file("client_secret.json"))}"
    global_tags                 = "${data.terraform_remote_state.shared.global_tags}"
}

module "ssm_google_auth_service_account" {
    source                      = "../../modules/ssm"
    service_name                = "team2-ssm-google-auth-service_account"
    qualified_path_to_outputs   = "/team2/global/ssm/google_auth_service_account"
    terraform_outputs           = "${map("google_auth_service_account", file("service-account.json"))}"
    global_tags                 = "${data.terraform_remote_state.shared.global_tags}"
}
