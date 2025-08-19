terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

variable "aws_region" {
  default = "us-east-1"
}

variable "project_name" {
  default = "test-api"
}

# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = var.project_name
}

# ECS Task Definition
resource "aws_ecs_task_definition" "app" {
  family                   = var.project_name
  network_mode            = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                     = "256"
  memory                  = "512"
  
  container_definitions = jsonencode([{
    name  = var.project_name
    image = "${var.project_name}:latest"
    
    portMappings = [{
      containerPort = 8000
      protocol      = "tcp"
    }]
  }])
}
