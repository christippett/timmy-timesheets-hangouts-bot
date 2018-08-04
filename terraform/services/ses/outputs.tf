###########################################################

#### KMS

output "ses_ssm_kms_key_id" {
    value = "${module.ssm_ses.kms_key_id}"
}

output "ses_ssm_kms_key_arn" {
    value = "${module.ssm_ses.kms_key_arn}"
}

###########################################################

#### SES

output "ses_identity_arn" {
    value = "${aws_ses_domain_identity.ses.arn}"
}
