output "r53_primary_zone_id" {
    value = "${aws_route53_zone.primary.zone_id}"
}

output "r53_primary_name_servers" {
    value = "${aws_route53_zone.primary.name_servers}"
}

output "r53_primary_zone_name" {
    value = "${aws_route53_zone.primary.name}"
}

output "apig_id" {
    value = "${aws_api_gateway_domain_name.apig.id}"
}

output "apig_expiration_date" {
    value = "${aws_api_gateway_domain_name.apig.id}"
}
