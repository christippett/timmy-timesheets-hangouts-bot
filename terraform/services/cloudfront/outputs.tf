output "website_cdn_hostname" {
  value = "${aws_cloudfront_distribution.website_cdn.domain_name}"
}

output "route53_website_alias_name" {
    value = "${aws_route53_record.cdn-alias.name}"
}