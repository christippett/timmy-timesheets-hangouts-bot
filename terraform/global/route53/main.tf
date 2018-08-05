terraform {
    required_version        = ">=0.11.7"

    backend "s3" {
        bucket              = "team2-terralock"
        key                 = "Team2/terraform/global/route53/terraform.tfstate"
        region              = "ap-southeast-2"
        encrypt             = "true"
        dynamodb_table      = "team2-terralocker"
    }
}

provider "aws" {
    region = "ap-southeast-2"
    profile = "team2servian"
}

resource "aws_route53_zone" "primary" {
    name = "timesheets.servian.fun"
    tags = "${data.terraform_remote_state.shared.global_tags}"
}

resource "aws_api_gateway_domain_name" "apig" {
  domain_name = "api.timesheets.servian.fun"

  certificate_arn = "${data.terraform_remote_state.acm.acm_cert_arn}"
}

resource "aws_route53_record" "apig" {
    name = "${aws_api_gateway_domain_name.apig.domain_name}"
    type = "A"
    zone_id = "${aws_route53_zone.primary.zone_id}"

    alias {
        name                   = "${aws_api_gateway_domain_name.apig.cloudfront_domain_name}"
        zone_id                = "${aws_api_gateway_domain_name.apig.cloudfront_zone_id}"
        evaluate_target_health = false
    }
}

resource "aws_api_gateway_base_path_mapping" "apig" {
  api_id      = "${data.aws_api_gateway_rest_api.my_rest_api.id}"
  stage_name  = ""
  domain_name = "${aws_api_gateway_domain_name.apig.domain_name}"
}
