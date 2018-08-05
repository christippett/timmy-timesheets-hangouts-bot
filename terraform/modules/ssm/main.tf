provider "aws" {
    region = "ap-southeast-2"
    profile = "team2servian"
}

module "kms" {
    source          = "../kms"
    service_name    = "${var.service_name}"
    global_tags     = "${var.global_tags}"
}

# TODO: counditional module

resource "aws_ssm_parameter" "ssm_kms" {
    name            = "${var.qualified_path_to_outputs}"
    description     = "Parameter store entry for the ${var.service_name} terraform outputs"
    key_id          = "${module.kms.kms_key_id}"
    type            = "SecureString"

    value           = "${var.encode ? jsonencode(merge(var.terraform_outputs, map("kms_id", module.kms.kms_key_id, "kms_arn", module.kms.kms_key_arn))) : element(values(var.terraform_outputs), 0)}"

    tags            = "${merge(var.global_tags, map("Name", coalesce(var.service_name, "-ssm")))}"
}
