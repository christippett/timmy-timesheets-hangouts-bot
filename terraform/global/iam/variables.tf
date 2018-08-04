data "terraform_remote_state" "shared" {
    backend = "s3"
    config {
        bucket              = "team2-terralock"
        key                 = "Team2/terraform/shared/terraform.tfstate"
        region              = "ap-southeast-2"
    }
}

data "terraform_remote_state" "dynamodb" {
    backend = "s3"
    config {
        bucket              = "team2-terralock"
        key                 = "Team2/terraform/service/dynamodb/terraform.tfstate"
        region              = "ap-southeast-2"
    }
}

data "terraform_remote_state" "sqs" {
    backend = "s3"
    config {
        bucket              = "team2-terralock"
        key                 = "Team2/terraform/service/sqs/terraform.tfstate"
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

data "terraform_remote_state" "s3" {
    backend = "s3"
    config {
        bucket              = "team2-terralock"
        key                 = "Team2/terraform/global/S3/terraform.tfstate"
        region              = "ap-southeast-2"
    }
}

data "terraform_remote_state" "ssm" {
    backend = "s3"
    config {
        bucket              = "team2-terralock"
        key                 = "Team2/terraform/global/ssm/terraform.tfstate"
        region              = "ap-southeast-2"
    }
}

data "terraform_remote_state" "ses" {
    backend = "s3"
    config {
        bucket              = "team2-terralock"
        key                 = "Team2/terraform/service/ses/terraform.tfstate"
        region              = "ap-southeast-2"
    }
}
