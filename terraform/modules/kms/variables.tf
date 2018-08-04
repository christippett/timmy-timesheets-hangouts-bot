###########################################################

# Required variables

variable "service_name" {
    description = "Name of the relevant service the key and associated outputs relate to"
}

variable "global_tags" {
    description = "Global tags to be applied"
    type        = "map"
}
