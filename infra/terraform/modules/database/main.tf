variable "environment" {
  type = string
}

variable "vpc_id" {
  type = string
}

variable "private_subnet_ids" {
  type = list(string)
}

# Subnet Group for RDS
resource "aws_db_subnet_group" "rds" {
  name       = "sentinelforge-rds-subnet-group-${var.environment}"
  subnet_ids = var.private_subnet_ids

  tags = {
    Name = "sentinelforge-rds-subnet-group"
  }
}

# Security Group for Database
resource "aws_security_group" "rds" {
  name        = "sentinelforge-rds-sg-${var.environment}"
  description = "Allow inbound PostgreSQL traffic from ECS compute only"
  vpc_id      = var.vpc_id

  ingress {
    description = "PostgreSQL from VPC private compute"
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/16"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# RDS PostgreSQL Instance
resource "aws_db_instance" "postgres" {
  identifier             = "sentinelforge-db-${var.environment}"
  engine                 = "postgres"
  engine_version         = "16.1"
  instance_class         = "db.t4g.medium"
  allocated_storage      = 50
  max_allocated_storage  = 200
  storage_type           = "gp3"
  storage_encrypted      = true
  db_name                = "sentinelforge"
  username               = "sentinel"
  manage_master_user_password = true
  db_subnet_group_name   = aws_db_subnet_group.rds.name
  vpc_security_group_ids = [aws_security_group.rds.id]
  skip_final_snapshot    = true
  multi_az               = var.environment == "prod" ? true : false
  deletion_protection    = var.environment == "prod" ? true : false

  tags = {
    Name        = "sentinelforge-postgres-${var.environment}"
    Environment = var.environment
  }
}

output "endpoint" {
  value = aws_db_instance.postgres.endpoint
}
