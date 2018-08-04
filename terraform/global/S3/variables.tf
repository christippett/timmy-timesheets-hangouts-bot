data "terraform_remote_state" "shared" {
    backend = "s3"
    config {
        bucket              = "team2-terralock"
        key                 = "Team2/terraform/shared/terraform.tfstate"
        region              = "ap-southeast-2"
    }
}

data "terraform_remote_state" "kms" {
    backend = "s3"
    config {
        bucket              = "team2-terralock"
        key                 = "Team2/terraform/global/kms/terraform.tfstate"
        region              = "ap-southeast-2"
    }
}
