terraform {
    required_version        = ">=0.11.7"

    backend "s3" {
        bucket              = "team2-terralock"
        key                 = "Team2/terraform/service/ses/terraform.tfstate"
        region              = "ap-southeast-2"
        encrypt             = "true"
        dynamodb_table      = "team2-terralocker"
    }
}

provider "aws" {
    region  = "us-east-1"
    profile = "team2servian"
}


resource "aws_ses_domain_mail_from" "ses" {
    domain           = "${aws_ses_domain_identity.ses.domain}"
    mail_from_domain = "email.${aws_ses_domain_identity.ses.domain}"
}

resource "aws_ses_domain_identity" "ses" {
    domain = "${data.terraform_remote_state.route53.r53_primary_zone_name}"
}

resource "aws_route53_record" "ses_verification" {
    zone_id = "${data.terraform_remote_state.route53.r53_primary_zone_id}"
    name    = "_amazonses.${data.terraform_remote_state.route53.r53_primary_zone_name}"
    type    = "TXT"
    ttl     = "600"
    records = ["${aws_ses_domain_identity.ses.verification_token}"]
}

resource "aws_ses_domain_identity_verification" "ses_verification" {
    domain = "${aws_ses_domain_identity.ses.id}"

    depends_on = ["aws_route53_record.ses_verification"]
}

# Example Route53 MX record
resource "aws_route53_record" "ses_domain_mail_from_mx" {
  zone_id = "${data.terraform_remote_state.route53.r53_primary_zone_id}"
  name    = "${aws_ses_domain_mail_from.ses.mail_from_domain}"
  type    = "MX"
  ttl     = "600"
  records = ["10 feedback-smtp.us-east-1.amazonses.com"] # Change to the region in which `aws_ses_domain_identity.example` is created
}

# Example Route53 TXT record for SPF
resource "aws_route53_record" "ses_domain_mail_from_txt" {
  zone_id = "${data.terraform_remote_state.route53.r53_primary_zone_id}"
  name    = "${aws_ses_domain_mail_from.ses.mail_from_domain}"
  type    = "TXT"
  ttl     = "600"
  records = ["v=spf1 include:amazonses.com -all"]
}


module "ssm_ses" {
    source                      = "../../modules/ssm"
    service_name                = "team2-ses"
    qualified_path_to_outputs   = "/team2/service/ses/ses_terraform_outputs"
    terraform_outputs           = "${map()}"
    global_tags                 = "${data.terraform_remote_state.shared.global_tags}"
}
