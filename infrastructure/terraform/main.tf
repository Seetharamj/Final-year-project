# Multi-Region Cloud Infrastructure
# Based on Disaster Risk Science Framework (Shi et al., 2020)
# Simplified working version without external module dependencies

terraform {
  required_version = ">= 1.5.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# Provider configurations for multi-region deployment
# Geographical Environment (E) component of disaster system

provider "aws" {
  alias  = "primary"
  region = var.primary_region
  
  default_tags {
    tags = {
      Project     = "AI-Driven-Disaster-Recovery"
      Environment = "production"
      ManagedBy   = "Terraform"
      Framework   = "Disaster-Risk-Science"
    }
  }
}

provider "aws" {
  alias  = "secondary"
  region = var.secondary_region
  
  default_tags {
    tags = {
      Project     = "AI-Driven-Disaster-Recovery"
      Environment = "production"
      ManagedBy   = "Terraform"
      Framework   = "Disaster-Risk-Science"
    }
  }
}

provider "aws" {
  alias  = "dr"
  region = var.dr_region
  
  default_tags {
    tags = {
      Project     = "AI-Driven-Disaster-Recovery"
      Environment = "production"
      ManagedBy   = "Terraform"
      Framework   = "Disaster-Risk-Science"
    }
  }
}

# Variables
variable "primary_region" {
  description = "Primary AWS region"
  type        = string
  default     = "us-east-1"
}

variable "secondary_region" {
  description = "Secondary AWS region for failover"
  type        = string
  default     = "us-west-2"
}

variable "dr_region" {
  description = "Disaster recovery region"
  type        = string
  default     = "eu-west-1"
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "ai-disaster-recovery"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

# Local variables
locals {
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# Data sources
data "aws_availability_zones" "primary" {
  provider = aws.primary
  state    = "available"
}

data "aws_availability_zones" "secondary" {
  provider = aws.secondary
  state    = "available"
}

data "aws_availability_zones" "dr" {
  provider = aws.dr
  state    = "available"
}

#############################################
# PRIMARY REGION INFRASTRUCTURE
#############################################

# VPC for Primary Region
resource "aws_vpc" "primary" {
  provider             = aws.primary
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  tags = merge(local.common_tags, {
    Name   = "${var.project_name}-primary-vpc"
    Region = "primary"
    Role   = "active"
  })
}

# Subnets for Primary Region
resource "aws_subnet" "primary_public" {
  provider                = aws.primary
  count                   = 2
  vpc_id                  = aws_vpc.primary.id
  cidr_block              = "10.0.${count.index}.0/24"
  availability_zone       = data.aws_availability_zones.primary.names[count.index]
  map_public_ip_on_launch = true
  
  tags = merge(local.common_tags, {
    Name = "${var.project_name}-primary-public-${count.index + 1}"
    Type = "public"
  })
}

resource "aws_subnet" "primary_private" {
  provider          = aws.primary
  count             = 2
  vpc_id            = aws_vpc.primary.id
  cidr_block        = "10.0.${count.index + 10}.0/24"
  availability_zone = data.aws_availability_zones.primary.names[count.index]
  
  tags = merge(local.common_tags, {
    Name = "${var.project_name}-primary-private-${count.index + 1}"
    Type = "private"
  })
}

# Internet Gateway for Primary
resource "aws_internet_gateway" "primary" {
  provider = aws.primary
  vpc_id   = aws_vpc.primary.id
  
  tags = merge(local.common_tags, {
    Name = "${var.project_name}-primary-igw"
  })
}

# Route Table for Primary
resource "aws_route_table" "primary_public" {
  provider = aws.primary
  vpc_id   = aws_vpc.primary.id
  
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.primary.id
  }
  
  tags = merge(local.common_tags, {
    Name = "${var.project_name}-primary-public-rt"
  })
}

resource "aws_route_table_association" "primary_public" {
  provider       = aws.primary
  count          = 2
  subnet_id      = aws_subnet.primary_public[count.index].id
  route_table_id = aws_route_table.primary_public.id
}

#############################################
# SECONDARY REGION INFRASTRUCTURE
#############################################

# VPC for Secondary Region
resource "aws_vpc" "secondary" {
  provider             = aws.secondary
  cidr_block           = "10.1.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  tags = merge(local.common_tags, {
    Name   = "${var.project_name}-secondary-vpc"
    Region = "secondary"
    Role   = "standby"
  })
}

# Subnets for Secondary Region
resource "aws_subnet" "secondary_public" {
  provider                = aws.secondary
  count                   = 2
  vpc_id                  = aws_vpc.secondary.id
  cidr_block              = "10.1.${count.index}.0/24"
  availability_zone       = data.aws_availability_zones.secondary.names[count.index]
  map_public_ip_on_launch = true
  
  tags = merge(local.common_tags, {
    Name = "${var.project_name}-secondary-public-${count.index + 1}"
    Type = "public"
  })
}

resource "aws_subnet" "secondary_private" {
  provider          = aws.secondary
  count             = 2
  vpc_id            = aws_vpc.secondary.id
  cidr_block        = "10.1.${count.index + 10}.0/24"
  availability_zone = data.aws_availability_zones.secondary.names[count.index]
  
  tags = merge(local.common_tags, {
    Name = "${var.project_name}-secondary-private-${count.index + 1}"
    Type = "private"
  })
}

# Internet Gateway for Secondary
resource "aws_internet_gateway" "secondary" {
  provider = aws.secondary
  vpc_id   = aws_vpc.secondary.id
  
  tags = merge(local.common_tags, {
    Name = "${var.project_name}-secondary-igw"
  })
}

# Route Table for Secondary
resource "aws_route_table" "secondary_public" {
  provider = aws.secondary
  vpc_id   = aws_vpc.secondary.id
  
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.secondary.id
  }
  
  tags = merge(local.common_tags, {
    Name = "${var.project_name}-secondary-public-rt"
  })
}

resource "aws_route_table_association" "secondary_public" {
  provider       = aws.secondary
  count          = 2
  subnet_id      = aws_subnet.secondary_public[count.index].id
  route_table_id = aws_route_table.secondary_public.id
}

#############################################
# DR REGION INFRASTRUCTURE
#############################################

# VPC for DR Region
resource "aws_vpc" "dr" {
  provider             = aws.dr
  cidr_block           = "10.2.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  tags = merge(local.common_tags, {
    Name   = "${var.project_name}-dr-vpc"
    Region = "dr"
    Role   = "cold-standby"
  })
}

# Subnets for DR Region
resource "aws_subnet" "dr_public" {
  provider                = aws.dr
  count                   = 2
  vpc_id                  = aws_vpc.dr.id
  cidr_block              = "10.2.${count.index}.0/24"
  availability_zone       = data.aws_availability_zones.dr.names[count.index]
  map_public_ip_on_launch = true
  
  tags = merge(local.common_tags, {
    Name = "${var.project_name}-dr-public-${count.index + 1}"
    Type = "public"
  })
}

#############################################
# STORAGE WITH CROSS-REGION REPLICATION
#############################################

# Primary S3 Bucket
resource "aws_s3_bucket" "primary" {
  provider = aws.primary
  bucket   = "${var.project_name}-primary-${var.environment}"
  
  tags = merge(local.common_tags, {
    Region = "primary"
  })
}

resource "aws_s3_bucket_versioning" "primary" {
  provider = aws.primary
  bucket   = aws_s3_bucket.primary.id
  
  versioning_configuration {
    status = "Enabled"
  }
}

# Secondary S3 Bucket (Replication Target)
resource "aws_s3_bucket" "secondary" {
  provider = aws.secondary
  bucket   = "${var.project_name}-secondary-${var.environment}"
  
  tags = merge(local.common_tags, {
    Region = "secondary"
  })
}

resource "aws_s3_bucket_versioning" "secondary" {
  provider = aws.secondary
  bucket   = aws_s3_bucket.secondary.id
  
  versioning_configuration {
    status = "Enabled"
  }
}

# IAM Role for S3 Replication
resource "aws_iam_role" "replication" {
  provider = aws.primary
  name     = "${var.project_name}-s3-replication-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "s3.amazonaws.com"
        }
      }
    ]
  })
  
  tags = local.common_tags
}

resource "aws_iam_role_policy" "replication" {
  provider = aws.primary
  name     = "${var.project_name}-s3-replication-policy"
  role     = aws_iam_role.replication.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "s3:GetReplicationConfiguration",
          "s3:ListBucket"
        ]
        Effect = "Allow"
        Resource = [
          aws_s3_bucket.primary.arn
        ]
      },
      {
        Action = [
          "s3:GetObjectVersionForReplication",
          "s3:GetObjectVersionAcl"
        ]
        Effect = "Allow"
        Resource = [
          "${aws_s3_bucket.primary.arn}/*"
        ]
      },
      {
        Action = [
          "s3:ReplicateObject",
          "s3:ReplicateDelete"
        ]
        Effect = "Allow"
        Resource = [
          "${aws_s3_bucket.secondary.arn}/*"
        ]
      }
    ]
  })
}

# S3 Replication Configuration
resource "aws_s3_bucket_replication_configuration" "primary_to_secondary" {
  provider = aws.primary
  role     = aws_iam_role.replication.arn
  bucket   = aws_s3_bucket.primary.id
  
  rule {
    id     = "replicate-all"
    status = "Enabled"
    
    destination {
      bucket        = aws_s3_bucket.secondary.arn
      storage_class = "STANDARD"
    }
  }
  
  depends_on = [
    aws_s3_bucket_versioning.primary,
    aws_s3_bucket_versioning.secondary
  ]
}

#############################################
# MONITORING AND ALERTING
#############################################

# SNS Topic for Disaster Alerts
resource "aws_sns_topic" "disaster_alerts" {
  provider = aws.primary
  name     = "${var.project_name}-disaster-alerts"
  
  tags = merge(local.common_tags, {
    Component = "alerting"
  })
}

# CloudWatch Alarm for Primary Region Health
resource "aws_cloudwatch_metric_alarm" "primary_health" {
  provider            = aws.primary
  alarm_name          = "${var.project_name}-primary-health"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "HealthyHostCount"
  namespace           = "AWS/NetworkELB"
  period              = "60"
  statistic           = "Average"
  threshold           = "1"
  alarm_description   = "This metric monitors primary region health"
  alarm_actions       = [aws_sns_topic.disaster_alerts.arn]
  
  tags = local.common_tags
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "disaster_recovery" {
  provider          = aws.primary
  name              = "/aws/${var.project_name}/disaster-recovery"
  retention_in_days = 30
  
  tags = local.common_tags
}

#############################################
# OUTPUTS
#############################################

output "primary_region_info" {
  description = "Primary region infrastructure information"
  value = {
    region     = var.primary_region
    vpc_id     = aws_vpc.primary.id
    vpc_cidr   = aws_vpc.primary.cidr_block
    subnet_ids = aws_subnet.primary_public[*].id
    s3_bucket  = aws_s3_bucket.primary.id
  }
}

output "secondary_region_info" {
  description = "Secondary region infrastructure information"
  value = {
    region     = var.secondary_region
    vpc_id     = aws_vpc.secondary.id
    vpc_cidr   = aws_vpc.secondary.cidr_block
    subnet_ids = aws_subnet.secondary_public[*].id
    s3_bucket  = aws_s3_bucket.secondary.id
  }
}

output "dr_region_info" {
  description = "DR region infrastructure information"
  value = {
    region     = var.dr_region
    vpc_id     = aws_vpc.dr.id
    vpc_cidr   = aws_vpc.dr.cidr_block
    subnet_ids = aws_subnet.dr_public[*].id
  }
}

output "disaster_recovery_endpoints" {
  description = "Disaster recovery system endpoints"
  value = {
    alert_topic_arn = aws_sns_topic.disaster_alerts.arn
    log_group_name  = aws_cloudwatch_log_group.disaster_recovery.name
    primary_bucket  = aws_s3_bucket.primary.bucket
    replica_bucket  = aws_s3_bucket.secondary.bucket
  }
}

output "replication_status" {
  description = "Cross-region replication configuration"
  value = {
    enabled         = true
    source_bucket   = aws_s3_bucket.primary.bucket
    source_region   = var.primary_region
    target_bucket   = aws_s3_bucket.secondary.bucket
    target_region   = var.secondary_region
    replication_role = aws_iam_role.replication.arn
  }
}
