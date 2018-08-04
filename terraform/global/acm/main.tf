terraform {
    required_version        = ">=0.11.7"

    backend "s3" {
        bucket              = "team2-terralock"
        key                 = "Team2/terraform/global/acm/terraform.tfstate"
        region              = "ap-southeast-2"
        encrypt             = "true"
        dynamodb_table      = "team2-terralocker"
    }
}

provider "aws" {
    region = "us-east-1"
    profile = "team2servian"
}

resource "aws_acm_certificate" "cert" {
  domain_name = "${data.terraform_remote_state.route53.r53_primary_zone_name}"
  validation_method = "DNS"
}

resource "aws_acm_certificate_validation" "cert" {
  certificate_arn = "${aws_acm_certificate.cert.arn}"
  validation_record_fqdns = ["${aws_route53_record.cert_validation.fqdn}"]
}

module "ssm_acm" {
    source                      = "../../modules/ssm"
    service_name                = "team2-kms-acm"
    qualified_path_to_outputs   = "/team2/global/acm/acm_terraform_outputs"
    terraform_outputs           = "${map("acm-arn", aws_acm_certificate.cert.arn, "acm-id", aws_acm_certificate.cert.id)}"
    global_tags                 = "${data.terraform_remote_state.shared.global_tags}"
}

