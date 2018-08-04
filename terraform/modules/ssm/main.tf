module "kms" {
    source          = "../kms"
    service_name    = "kms-${var.service_name}"
    global_tags     = "${var.global_tags}"
}

resource "aws_ssm_parameter" "ssm_kms" {
    name            = "${var.qualified_path_to_outputs}"
    description     = "Parameter store entry for the ${var.service_name} terraform outputs"
    key_id          = "${module.kms.kms_key_id}"
    type            = "SecureString"

    value           = "${jsonencode(merge(var.terraform_outputs, map("kms_id", module.kms.kms_key_id, "kms_arn", module.kms.kms_key_arn)))}"

    tags            = "${merge(var.global_tags, map("Name", coalesce(var.service_name, "-ssm")))}"
}
