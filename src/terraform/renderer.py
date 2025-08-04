"""
Terraform Template Renderer
Renders Jinja2 templates into Terraform configurations based on deployment specifications.
"""

import os
import json
from typing import Dict, Any
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
import logging

logger = logging.getLogger(__name__)


class TerraformRenderer:
    """Renders Terraform configurations from Jinja2 templates."""
    
    def __init__(self, templates_dir: str = None):
        """
        Initialize the renderer with templates directory.
        
        Args:
            templates_dir: Path to Jinja2 templates directory
        """
        if templates_dir is None:
            templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
        
        self.templates_dir = Path(templates_dir)
        if not self.templates_dir.exists():
            raise FileNotFoundError(f"Templates directory not found: {templates_dir}")
        
        # Set up Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Add custom filters
        self.env.filters['to_json'] = json.dumps
    
    def render_configuration(self, spec: Dict[str, Any], output_dir: str = None) -> Dict[str, str]:
        """
        Render complete Terraform configuration based on deployment specification.
        
        Args:
            spec: Deployment specification from analyzer
            output_dir: Optional output directory to write files
            
        Returns:
            Dict mapping filenames to rendered content
        """
        logger.info(f"Rendering Terraform configuration for: {spec}")
        
        rendered_files = {}
        
        # Always render provider configuration
        rendered_files['provider.tf'] = self._render_provider(spec)
        
        # Render based on infrastructure type
        infra_type = spec.get('infra_type', 'vm')
        
        if infra_type == 'vm':
            rendered_files.update(self._render_vm_configuration(spec))
        elif infra_type == 'serverless':
            rendered_files.update(self._render_serverless_configuration(spec))
        elif infra_type == 'container':
            rendered_files.update(self._render_container_configuration(spec))
        
        # Render common resources
        rendered_files.update(self._render_common_resources(spec))
        
        # Write files if output directory specified
        if output_dir:
            self._write_files(rendered_files, output_dir)
        
        logger.info(f"Rendered {len(rendered_files)} files")
        return rendered_files
    
    def _render_provider(self, spec: Dict[str, Any]) -> str:
        """Render provider configuration."""
        try:
            template = self.env.get_template('provider.tf.j2')
            return template.render(spec=spec)
        except TemplateNotFound:
            # Fallback provider configuration
            return self._get_fallback_provider(spec)
    
    def _render_vm_configuration(self, spec: Dict[str, Any]) -> Dict[str, str]:
        """Render VM-specific resources."""
        files = {}
        
        try:
            # Main VM configuration
            template = self.env.get_template('vm.tf.j2')
            files['vm.tf'] = template.render(spec=spec)
        except TemplateNotFound:
            files['vm.tf'] = self._get_fallback_vm_config(spec)
        
        # Network configuration
        files['network.tf'] = self._render_network_config(spec)
        
        # Security groups
        files['security.tf'] = self._render_security_config(spec)
        
        return files
    
    def _render_serverless_configuration(self, spec: Dict[str, Any]) -> Dict[str, str]:
        """Render serverless-specific resources."""
        files = {}
        
        try:
            template = self.env.get_template('serverless.tf.j2')
            files['lambda.tf'] = template.render(spec=spec)
        except TemplateNotFound:
            files['lambda.tf'] = self._get_fallback_lambda_config(spec)
        
        # IAM role for Lambda
        files['iam.tf'] = self._render_lambda_iam(spec)
        
        return files
    
    def _render_container_configuration(self, spec: Dict[str, Any]) -> Dict[str, str]:
        """Render container-specific resources (ECS)."""
        files = {}
        
        # ECS cluster and service
        files['ecs.tf'] = self._render_ecs_config(spec)
        
        # Application Load Balancer if needed
        if spec.get('load_balancer_required', False):
            files['alb.tf'] = self._render_alb_config(spec)
        
        return files
    
    def _render_common_resources(self, spec: Dict[str, Any]) -> Dict[str, str]:
        """Render common resources like outputs and variables."""
        files = {}
        
        # Variables
        files['variables.tf'] = self._render_variables(spec)
        
        # Outputs
        files['outputs.tf'] = self._render_outputs(spec)
        
        return files
    
    def _render_network_config(self, spec: Dict[str, Any]) -> str:
        """Render VPC and networking configuration."""
        network_config = spec.get('network', {})
        
        return f'''# VPC Configuration
resource "aws_vpc" "main" {{
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  tags = {{
    Name        = "{spec.get('framework', 'app')}-vpc"
    Environment = "{spec.get('environment', 'dev')}"
  }}
}}

# Internet Gateway
resource "aws_internet_gateway" "main" {{
  vpc_id = aws_vpc.main.id
  
  tags = {{
    Name = "{spec.get('framework', 'app')}-igw"
  }}
}}

# Public Subnet
resource "aws_subnet" "public" {{
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = data.aws_availability_zones.available.names[0]
  map_public_ip_on_launch = true
  
  tags = {{
    Name = "{spec.get('framework', 'app')}-public-subnet"
  }}
}}

# Route Table
resource "aws_route_table" "public" {{
  vpc_id = aws_vpc.main.id
  
  route {{
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }}
  
  tags = {{
    Name = "{spec.get('framework', 'app')}-public-rt"
  }}
}}

# Route Table Association
resource "aws_route_table_association" "public" {{
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}}

# Data source for availability zones
data "aws_availability_zones" "available" {{
  state = "available"
}}
'''
    
    def _render_security_config(self, spec: Dict[str, Any]) -> str:
        """Render security group configuration."""
        security = spec.get('security', {})
        ingress_rules = security.get('security_groups', {}).get('ingress_rules', [])
        
        ingress_blocks = []
        for rule in ingress_rules:
            ingress_blocks.append(f'''  ingress {{
    from_port   = {rule['port']}
    to_port     = {rule['port']}
    protocol    = "{rule['protocol']}"
    cidr_blocks = ["{rule['cidr']}"]
  }}''')
        
        ingress_content = '\n'.join(ingress_blocks)
        
        return f'''# Security Group
resource "aws_security_group" "main" {{
  name_prefix = "{spec.get('framework', 'app')}-sg"
  vpc_id      = aws_vpc.main.id
  
{ingress_content}
  
  egress {{
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }}
  
  tags = {{
    Name = "{spec.get('framework', 'app')}-security-group"
  }}
}}
'''
    
    def _render_variables(self, spec: Dict[str, Any]) -> str:
        """Render variables.tf file."""
        return '''# Variables
variable "region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "aws_access_key" {
  description = "AWS access key"
  type        = string
  sensitive   = true
}

variable "aws_secret_key" {
  description = "AWS secret key"
  type        = string
  sensitive   = true
}

variable "aws_endpoint_url" {
  description = "AWS endpoint URL for LocalStack"
  type        = string
  default     = "http://localhost:4566"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "dev"
}
'''
    
    def _render_outputs(self, spec: Dict[str, Any]) -> str:
        """Render outputs.tf file."""
        infra_type = spec.get('infra_type', 'vm')
        
        outputs = ['# Outputs']
        
        if infra_type == 'vm':
            outputs.extend([
                'output "instance_ip" {',
                '  description = "Public IP of the EC2 instance"',
                '  value       = aws_instance.main.public_ip',
                '}',
                '',
                'output "instance_dns" {',
                '  description = "Public DNS of the EC2 instance"',
                '  value       = aws_instance.main.public_dns',
                '}'
            ])
        elif infra_type == 'serverless':
            outputs.extend([
                'output "lambda_function_name" {',
                '  description = "Name of the Lambda function"',
                '  value       = aws_lambda_function.main.function_name',
                '}',
                '',
                'output "lambda_function_arn" {',
                '  description = "ARN of the Lambda function"',
                '  value       = aws_lambda_function.main.arn',
                '}'
            ])
        
        return '\n'.join(outputs)
    
    def _get_fallback_provider(self, spec: Dict[str, Any]) -> str:
        """Get fallback provider configuration when template is missing."""
        return '''# Provider configuration
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
  region     = var.region
  access_key = var.aws_access_key
  secret_key = var.aws_secret_key
  
  # LocalStack configuration
  skip_credentials_validation = true
  skip_requesting_account_id  = true
  skip_metadata_api_check     = true

  endpoints {
    ec2 = var.aws_endpoint_url
    s3  = var.aws_endpoint_url
    iam = var.aws_endpoint_url
    lambda = var.aws_endpoint_url
  }
}
'''
    
    def _get_fallback_vm_config(self, spec: Dict[str, Any]) -> str:
        """Get fallback VM configuration when template is missing."""
        default_user_data = '#!/bin/bash\necho "Hello World"'
        user_data_script = spec.get('user_data_script', default_user_data)
        return f'''# EC2 Instance
resource "aws_instance" "main" {{
  ami           = data.aws_ami.ubuntu.id
  instance_type = "{spec.get('instance_type', 't3.micro')}"
  subnet_id     = aws_subnet.public.id
  vpc_security_group_ids = [aws_security_group.main.id]
  
  user_data = <<-EOF
{user_data_script}
  EOF
  
  tags = {{
    Name        = "{spec.get('framework', 'app')}-instance"
    Environment = "{spec.get('environment', 'dev')}"
  }}
}}

# AMI Data Source
data "aws_ami" "ubuntu" {{
  most_recent = true
  owners      = ["099720109477"] # Canonical
  
  filter {{
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }}
  
  filter {{
    name   = "virtualization-type"
    values = ["hvm"]
  }}
}}
'''
    
    def _get_fallback_lambda_config(self, spec: Dict[str, Any]) -> str:
        """Get fallback Lambda configuration when template is missing."""
        return f'''# Lambda Function
resource "aws_lambda_function" "main" {{
  filename         = "function.zip"
  function_name    = "{spec.get('framework', 'app')}-function"
  role            = aws_iam_role.lambda.arn
  handler         = "index.handler"
  runtime         = "{spec.get('runtime', 'nodejs18.x')}"
  timeout         = {spec.get('timeout_seconds', 30)}
  memory_size     = {spec.get('memory_mb', 512)}
  
  environment {{
    variables = {{
      ENVIRONMENT = "{spec.get('environment', 'dev')}"
      REGION     = "{spec.get('region', 'us-east-1')}"
    }}
  }}
  
  tags = {{
    Name        = "{spec.get('framework', 'app')}-lambda"
    Environment = "{spec.get('environment', 'dev')}"
  }}
}}
'''
    
    def _render_lambda_iam(self, spec: Dict[str, Any]) -> str:
        """Render IAM role for Lambda function."""
        return '''# IAM Role for Lambda
resource "aws_iam_role" "lambda" {
  name = "lambda-execution-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# IAM Role Policy Attachment
resource "aws_iam_role_policy_attachment" "lambda_basic" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  role       = aws_iam_role.lambda.name
}
'''
    
    def _render_ecs_config(self, spec: Dict[str, Any]) -> str:
        """Render ECS configuration for container deployments."""
        return f'''# ECS Cluster
resource "aws_ecs_cluster" "main" {{
  name = "{spec.get('framework', 'app')}-cluster"
  
  tags = {{
    Name        = "{spec.get('framework', 'app')}-cluster"
    Environment = "{spec.get('environment', 'dev')}"
  }}
}}

# ECS Task Definition
resource "aws_ecs_task_definition" "main" {{
  family                   = "{spec.get('framework', 'app')}-task"
  network_mode            = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                     = "{spec.get('container_cpu', 256)}"
  memory                  = "{spec.get('container_memory', 512)}"
  execution_role_arn      = aws_iam_role.ecs_execution.arn
  
  container_definitions = jsonencode([
    {{
      name  = "{spec.get('framework', 'app')}"
      image = "nginx:latest"
      portMappings = [
        {{
          containerPort = 80
          protocol      = "tcp"
        }}
      ]
      logConfiguration = {{
        logDriver = "awslogs"
        options = {{
          awslogs-group         = aws_cloudwatch_log_group.main.name
          awslogs-region        = "{spec.get('region', 'us-east-1')}"
          awslogs-stream-prefix = "ecs"
        }}
      }}
    }}
  ])
}}

# ECS Service
resource "aws_ecs_service" "main" {{
  name            = "{spec.get('framework', 'app')}-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.main.arn
  desired_count   = {spec.get('desired_count', 1)}
  launch_type     = "FARGATE"
  
  network_configuration {{
    subnets         = [aws_subnet.public.id]
    security_groups = [aws_security_group.main.id]
    assign_public_ip = true
  }}
}}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "main" {{
  name              = "/ecs/{spec.get('framework', 'app')}"
  retention_in_days = {spec.get('monitoring', {}).get('log_retention_days', 7)}
}}

# ECS Execution Role
resource "aws_iam_role" "ecs_execution" {{
  name = "ecs-execution-role"
  
  assume_role_policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [
      {{
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {{
          Service = "ecs-tasks.amazonaws.com"
        }}
      }}
    ]
  }})
}}

resource "aws_iam_role_policy_attachment" "ecs_execution" {{
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
  role       = aws_iam_role.ecs_execution.name
}}
'''
    
    def _render_alb_config(self, spec: Dict[str, Any]) -> str:
        """Render Application Load Balancer configuration."""
        return f'''# Application Load Balancer
resource "aws_lb" "main" {{
  name               = "{spec.get('framework', 'app')}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets           = [aws_subnet.public.id]
  
  tags = {{
    Name        = "{spec.get('framework', 'app')}-alb"
    Environment = "{spec.get('environment', 'dev')}"
  }}
}}

# ALB Target Group
resource "aws_lb_target_group" "main" {{
  name        = "{spec.get('framework', 'app')}-tg"
  port        = 80
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"
  
  health_check {{
    enabled             = true
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 5
    interval            = 30
    path                = "/"
    matcher             = "200"
  }}
}}

# ALB Listener
resource "aws_lb_listener" "main" {{
  load_balancer_arn = aws_lb.main.arn
  port              = "80"
  protocol          = "HTTP"
  
  default_action {{
    type             = "forward"
    target_group_arn = aws_lb_target_group.main.arn
  }}
}}

# Security Group for ALB
resource "aws_security_group" "alb" {{
  name_prefix = "{spec.get('framework', 'app')}-alb-sg"
  vpc_id      = aws_vpc.main.id
  
  ingress {{
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }}
  
  egress {{
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }}
}}
'''
    
    def _write_files(self, files: Dict[str, str], output_dir: str) -> None:
        """Write rendered files to output directory."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        for filename, content in files.items():
            file_path = output_path / filename
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"Written: {file_path}")


def render_configuration(spec: Dict[str, Any], output_dir: str = None) -> Dict[str, str]:
    """Convenience function for rendering configurations."""
    renderer = TerraformRenderer()
    return renderer.render_configuration(spec, output_dir)