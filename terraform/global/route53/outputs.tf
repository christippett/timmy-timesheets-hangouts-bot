output "r53_primary_zone_id" {
    value = "${aws_route53_zone.primary.zone_id}"
}

output "53_primary_name_servers" {
    value = "${aws_route53_zone.primary.name_servers}"
}