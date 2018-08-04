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

# NOTE: If we have a private hosted zone or domain is needed
# then they go here. Otherwise then entries for each relevant
# service

resource "aws_route53_zone" "primary" {
    name = "timesheets.servian.fun"
    tags = "${data.terraform_remote_state.shared.global_tags}"
}

resource "aws_route53_record" "apig" {
    name = "api.timesheets.servian.fun"
    type = "A"
    zone_id = "${aws_route53_zone.primary.zone_id}"
    # Hardcoded API Gateway record
    records = ["https://sdr1ekqn43.execute-api.ap-southeast-2.amazonaws.com"]
    ttl = 60
}
