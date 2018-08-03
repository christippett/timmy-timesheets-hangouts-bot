data "aws_caller_identity" "current" {}

variable "global_tags" {
    type = "map"
    default {
        "Environment" = "Servian"
        "Team" = "Team2"
    }
}

variable "region" {
    default = "ap-southeast-2"
}
