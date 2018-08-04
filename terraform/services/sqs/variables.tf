data "terraform_remote_state" "shared" {
    backend = "s3"
    config {
        bucket              = "team2-terralock"
        key                 = "Team2/terraform/shared/terraform.tfstate"
        region              = "ap-southeast-2"
    }
}
