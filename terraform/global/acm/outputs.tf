###########################################################

## ACM

output "acm_cert_id" {
    value = "${aws_acm_certificate.cert.id}"
}

output "acm_cert_arn" {
    value = "${aws_acm_certificate.cert.arn}"
}

output "acm_cert_domain_validation_options" {
    value = "${aws_acm_certificate.cert.domain_validation_options}"
}

## KMS 

output "acm_kms_key_id" {
    value = "${module.ssm_acm.kms_key_id}"
}

output "acm_kms_key_arn" {
    value = "${module.ssm_acm.kms_key_arn}"
}
