output "account_id" {
    value       = "${data.aws_caller_identity.current.account_id}"
}

output "global_tags" {
    value       = "${var.global_tags}"
}

output "region" {
    value       = "${var.region}"
}
