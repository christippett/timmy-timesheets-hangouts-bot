###########################################################

#### KMS

output "sqs_chat_kms_key_id" {
    value = "${module.kms_sqs_chat.kms_key_id}"
}

output "sqs_chat_kms_key_arn" {
    value = "${module.kms_sqs_chat.kms_key_arn}"
}

output "sqs_scrape_kms_key_id" {
    value = "${module.kms_sqs_scrape.kms_key_id}"
}

output "sqs_scrape_kms_key_arn" {
    value = "${module.kms_sqs_scrape.kms_key_arn}"
}

output "sqs_process_kms_key_id" {
    value = "${module.kms_sqs_process.kms_key_id}"
}

output "sqs_process_kms_key_arn" {
    value = "${module.kms_sqs_process.kms_key_arn}"
}

output "sqs_ssm_kms_key_id" {
    value = "${module.ssm_sqs.kms_key_id}"
}

output "sqs_ssm_kms_key_arn" {
    value = "${module.ssm_sqs.kms_key_arn}"
}

###########################################################

#### SQS

output "sqs_chat_arn" {
    value = "${aws_sqs_queue.sqs_queue_chat.arn}"
}

output "sqs_chat_id" {
    value = "${aws_sqs_queue.sqs_queue_chat.id}"
}

output "sqs_scrape_arn" {
    value = "${aws_sqs_queue.sqs_queue_scrape.arn}"
}

output "sqs_scrape_id" {
    value = "${aws_sqs_queue.sqs_queue_scrape.id}"
}

output "sqs_process_arn" {
    value = "${aws_sqs_queue.sqs_queue_process.arn}"
}

output "sqs_process_id" {
    value = "${aws_sqs_queue.sqs_queue_process.id}"
}
