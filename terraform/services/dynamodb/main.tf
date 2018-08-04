terraform {
    required_version        = ">=0.11.7"

    backend "s3" {
        bucket              = "team2-terralock"
        key                 = "Team2/terraform/service/dynamodb/terraform.tfstate"
        region              = "ap-southeast-2"
        encrypt             = "true"
        dynamodb_table      = "team2-terralocker"
    }
}

provider "aws" {
    region  = "ap-southeast-2"
    profile = "team2"
}

resource "aws_dynamodb_table" "user_register" {
    name           = "team2-user-register"
    read_capacity  = 20
    write_capacity = 20
    hash_key       = "UserId"

    # As this table is for storing registration details per user
    # including hashed credentials there is no real need for 
    # a range key or global or local secondary indexes

    attribute {
        name = "UserId"
        type = "S"
    }

    server_side_encryption {
        enabled = "true"
    }

    tags = "${data.terraform_remote_state.shared.global_tags}"
}

module "ssm_outputs_dynamoddb_user_register" {
    source                      = "../../modules/ssm"
    service_name                = "team2-dynamodb-table-user-register"
    qualified_path_to_outputs   = "/team2/service/dynamodb/dynamodb_terraform_outputs"
    terraform_outputs           = "${map("team2-user-register-arn", aws_dynamodb_table.user_register.arn, "team2-user-register-id", aws_dynamodb_table.user_register.id)}"
    global_tags                 = "${data.terraform_remote_state.shared.global_tags}"
}
