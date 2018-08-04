output "s3_kms_key_id" {
    value = "${module.kms-s3-app.kms_key_id}"
}

output "s3_kms_key_arn" {
    value = "${module.kms-s3-app.kms_key_arn}"
}
