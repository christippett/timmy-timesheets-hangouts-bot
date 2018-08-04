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
    profile = "team2"
}

# NOTE: If we have a private hosted zone or domain is needed
# then they go here. Otherwise then entries for each relevant
# service

resource "aws_route53_zone" "primary" {
    name = "timesheets.servian.fun"
    tags = "${data.terraform_remote_state.shared.global_tags}"
}
