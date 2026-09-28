terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "SentinelForge"
      Environment = "dev"
      ManagedBy   = "Terraform"
    }
  }
}

variable "aws_region" {
  type    = string
  default = "us-east-1"
}

module "networking" {
  source      = "../../modules/networking"
  environment = "dev"
}

module "database" {
  source             = "../../modules/database"
  environment        = "dev"
  vpc_id             = module.networking.vpc_id
  private_subnet_ids = module.networking.private_subnet_ids
}

module "iam" {
  source      = "../../modules/iam"
  environment = "dev"
}

output "vpc_id" {
  value = module.networking.vpc_id
}

output "database_endpoint" {
  value = module.database.endpoint
}
