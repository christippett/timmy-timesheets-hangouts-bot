###########################################################

# Required variables

variable "service_name" {
    description = "Name of the relevant service the key and associated outputs relate to"
}

variable "qualified_path_to_outputs" {
    description = "Qualified path to the parameter store location"
}

variable "terraform_outputs" {
    description = "The outputs from the relevant service"
    type        = "map"
}

variable "global_tags" {
    description = "Global tags to be applied"
    type        = "map"
}

# Defaulted variables

variable "encode" {
    default = true
}

