variable "aws_region" {
  description = "AWS region where infrastructure is created"
  type        = string
  default     = "ap-south-1"
}

variable "instance_name" {
  description = "Name tag for the EC2 instance"
  type        = string
  default     = "SmartAttendanceServer"
}

variable "instance_type" {
  description = "EC2 instance size"
  type        = string
  default     = "t3.micro"
}

variable "key_name" {
  description = "Prefix used for the Terraform-generated AWS key pair"
  type        = string
  default     = "attendance-key"
}

variable "repo_url" {
  description = "Git repository URL for the attendance app"
  type        = string
  default     = "https://github.com/priya0013/mini-project-safs"
}

variable "app_port" {
  description = "Application port exposed from EC2"
  type        = number
  default     = 5000
}

variable "ssh_cidr_blocks" {
  description = "CIDR ranges allowed to SSH into the server"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}
