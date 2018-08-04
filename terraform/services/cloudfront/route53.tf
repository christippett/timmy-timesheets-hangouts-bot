################################################################################################################
## Create a Route53 ALIAS record to the Cloudfront website distribution
################################################################################################################
resource "aws_route53_record" "cdn-alias" {
  zone_id = "${data.terraform_remote_state.route53.r53_primary_zone_id}"
  name    = "${data.terraform_remote_state.route53.r53_primary_zone_name}"
  type    = "A"

  alias {
    name                   = "${aws_cloudfront_distribution.website_cdn.domain_name}"
    zone_id                = "${aws_cloudfront_distribution.website_cdn.hosted_zone_id}"
    evaluate_target_health = false
  }
}

################################################################################################################
## Create a Route53 CNAME record to the Cloudfront distribution
################################################################################################################

# resource "aws_route53_record" "cdn-cname" {
#   zone_id = "${var.route53_zone_id}"
#   name    = "${var.domain}"
#   type    = "CNAME"
#   ttl     = "300"
#   records = ["${var.target}"]
# }