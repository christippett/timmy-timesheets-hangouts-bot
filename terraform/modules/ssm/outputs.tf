###########################################################

# KMS

output "kms_key_id" {
    value = "${module.kms.kms_key_id}"
}

output "kms_key_arn" {
    value = "${module.kms.kms_key_arn}"
}

###########################################################

# SSM

output "ssm_arn" {
    value = "${aws_ssm_parameter.ssm_kms.arn}"
}

output "ssm_name" {
    value = "${aws_ssm_parameter.ssm_kms.name}"
}
