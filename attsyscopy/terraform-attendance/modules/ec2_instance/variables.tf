variable "instance_name" {
  description = "Name tag for the EC2 instance"
  type        = string
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
}

variable "key_name" {
  description = "Prefix used for the Terraform-generated AWS key pair"
  type        = string
}

variable "repo_url" {
  description = "Git repository URL to clone during bootstrap"
  type        = string
}

variable "app_port" {
  description = "Application port exposed by the API"
  type        = number
}

variable "ssh_cidr_blocks" {
  description = "CIDR blocks allowed to SSH"
  type        = list(string)
}
