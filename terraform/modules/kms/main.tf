resource "aws_kms_key" "kms" {
    description             = "team2 - KMS Key for the ${var.service_name}"
    deletion_window_in_days = 10
    enable_key_rotation     = "true"

    tags                    = "${var.global_tags}"
}

resource "aws_kms_alias" "kms" {
    name                    = "alias/${var.service_name}-kms"
    target_key_id           = "${aws_kms_key.kms.key_id}"
}
