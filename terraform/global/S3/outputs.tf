output "website_bucket_arn" {
    value = "${aws_s3_bucket.website.arn}"
}

output "website_bucket_id" {
    value = "${aws_s3_bucket.website.id}"
}

output "website_endpoint" {
    value = "${aws_s3_bucket.website.website_endpoint}"
}

output "app_bucket_arn" {
    value = "${aws_s3_bucket.app.arn}"
}

output "app_bucket_id" {
    value = "${aws_s3_bucket.app.id}"
}

output "s3_ssm_kms_key_id" {
    value = "${module.ssm_kms_s3.kms_key_id}"
}

output "s3_ssm_kms_key_arn" {
    value = "${module.ssm_kms_s3.kms_key_arn}"
}
