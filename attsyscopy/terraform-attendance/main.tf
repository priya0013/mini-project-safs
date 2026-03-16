terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0"
    }
    local = {
      source  = "hashicorp/local"
      version = ">= 2.4"
    }
    tls = {
      source  = "hashicorp/tls"
      version = ">= 4.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

module "attendance_server" {
  source = "./modules/ec2_instance"

  instance_name   = var.instance_name
  instance_type   = var.instance_type
  key_name        = var.key_name
  repo_url        = var.repo_url
  app_port        = var.app_port
  ssh_cidr_blocks = var.ssh_cidr_blocks
}
