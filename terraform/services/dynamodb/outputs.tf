###########################################################

# Dynamo

output "dynamodb_team2_user_register_arn" {
    value = "${aws_dynamodb_table.user_register.arn}"
}

output "dynamodb_team2_user_register_id" {
    value = "${aws_dynamodb_table.user_register.id}"
}

###########################################################

# KMS

output "dynamodb_team2_user_register_kms_key_id" {
    value = "${module.ssm_outputs_dynamoddb_user_register.kms_key_id}"
}

output "dynamodb_team2_user_register_kms_key_arn" {
    value = "${module.ssm_outputs_dynamoddb_user_register.kms_key_arn}"
}

###########################################################

# SSM

output "dynamodb_team2_user_register_ssm_arn" {
    value = "${module.ssm_outputs_dynamoddb_user_register.ssm_arn}"
}

output "dynamodb_team2_user_register_ssm_name" {
    value = "${module.ssm_outputs_dynamoddb_user_register.ssm_name}"
}
