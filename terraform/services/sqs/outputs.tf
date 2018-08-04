###########################################################

#### KMS

output "sqs_kms_key_id" {
    value = "${module.kms_sqs.kms_key_id}"
}

output "sqs_kms_key_arn" {
    value = "${module.kms_sqs.kms_key_arn}"
}

output "sqs_ssm_kms_key_id" {
    value = "${module.ssm_sqs.kms_key_id}"
}

output "sqs_ssm_kms_key_arn" {
    value = "${module.ssm_sqs.kms_key_arn}"
}

###########################################################

#### SQS

output "sqs_arn" {
    value = "${aws_sqs_queue.sqs_queue.arn}"
}

output "sqs_id" {
    value = "${aws_sqs_queue.sqs_queue.id}"
}
