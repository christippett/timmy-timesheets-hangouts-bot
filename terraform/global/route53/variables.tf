data "terraform_remote_state" "shared" {
    backend = "s3"
    config {
        bucket              = "team2-terralock"
        key                 = "Team2/terraform/shared/terraform.tfstate"
        region              = "ap-southeast-2"
    }
}

data "terraform_remote_state" "acm" {
    backend = "s3"
    config {
        bucket              = "team2-terralock"
        key                 = "Team2/terraform/global/acm/terraform.tfstate"
        region              = "ap-southeast-2"
    }
}

data "aws_api_gateway_rest_api" "my_rest_api" {
  name = "timesheet-bot"
}
