###########################################################

# KMS

output "google_auth_client_secret_kms_key_id" {
    value = "${module.ssm_google_auth_client_secret.kms_key_id}"
}

output "google_auth_client_secret_kms_key_arn" {
    value = "${module.ssm_google_auth_client_secret.kms_key_arn}"
}

output "google_auth_service_account_kms_key_id" {
    value = "${module.ssm_google_auth_service_account.kms_key_id}"
}

output "google_auth_service_account_kms_key_arn" {
    value = "${module.ssm_google_auth_service_account.kms_key_arn}"
}

###########################################################

# SSM

output "google_auth_client_secret_ssm_arn" {
    value = "${module.ssm_google_auth_client_secret.ssm_arn}"
}

output "google_auth_client_secret_ssm_name" {
    value = "${module.ssm_google_auth_client_secret.ssm_name}"
}

output "google_auth_service_account_ssm_arn" {
    value = "${module.ssm_google_auth_service_account.ssm_arn}"
}

output "google_auth_service_account_ssm_name" {
    value = "${module.ssm_google_auth_service_account.ssm_name}"
}
