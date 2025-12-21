terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "ca-central-1"
}

############################################
# VPC
############################################
resource "aws_vpc" "project_vpc" {
  cidr_block           = "10.20.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "project_vpc"
  }
}

############################################
# SUBNETS
############################################
data "aws_availability_zones" "available" {}

resource "aws_subnet" "public_a" {
  vpc_id                  = aws_vpc.project_vpc.id
  cidr_block              = "10.20.2.0/24"
  availability_zone       = data.aws_availability_zones.available.names[0]
  map_public_ip_on_launch = true

  tags = { Name = "PublicSubnetA" }
}

resource "aws_subnet" "public_b" {
  vpc_id                  = aws_vpc.project_vpc.id
  cidr_block              = "10.20.4.0/24"
  availability_zone       = data.aws_availability_zones.available.names[1]
  map_public_ip_on_launch = true

  tags = { Name = "PublicSubnetB" }
}

resource "aws_subnet" "private_a" {
  vpc_id            = aws_vpc.project_vpc.id
  cidr_block        = "10.20.1.0/24"
  availability_zone = data.aws_availability_zones.available.names[0]

  tags = { Name = "PrivateSubnetA" }
}

resource "aws_subnet" "private_b" {
  vpc_id            = aws_vpc.project_vpc.id
  cidr_block        = "10.20.3.0/24"
  availability_zone = data.aws_availability_zones.available.names[1]

  tags = { Name = "PrivateSubnetB" }
}

############################################
# INTERNET GATEWAY
############################################
resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.project_vpc.id

  tags = {
    Name = "project-igw"
  }
}

############################################
# NAT GATEWAYS + EIPS
############################################
resource "aws_eip" "nat_a" {
  domain = "vpc"
}

resource "aws_nat_gateway" "nat_a" {
  allocation_id = aws_eip.nat_a.id
  subnet_id     = aws_subnet.public_a.id

  tags = { Name = "NAT-A" }
}

resource "aws_eip" "nat_b" {
  domain = "vpc"
}

resource "aws_nat_gateway" "nat_b" {
  allocation_id = aws_eip.nat_b.id
  subnet_id     = aws_subnet.public_b.id

  tags = { Name = "NAT-B" }
}

############################################
# ROUTE TABLES
############################################
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.project_vpc.id
}

resource "aws_route" "public_default_route" {
  route_table_id         = aws_route_table.public.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.igw.id
}

resource "aws_route_table" "private_a" {
  vpc_id = aws_vpc.project_vpc.id
}

resource "aws_route" "private_a_default" {
  route_table_id         = aws_route_table.private_a.id
  destination_cidr_block = "0.0.0.0/0"
  nat_gateway_id         = aws_nat_gateway.nat_a.id
}

resource "aws_route_table" "private_b" {
  vpc_id = aws_vpc.project_vpc.id
}

resource "aws_route" "private_b_default" {
  route_table_id         = aws_route_table.private_b.id
  destination_cidr_block = "0.0.0.0/0"
  nat_gateway_id         = aws_nat_gateway.nat_b.id
}

############################################
# ROUTE TABLE ASSOCIATIONS
############################################
resource "aws_route_table_association" "public_a" {
  subnet_id      = aws_subnet.public_a.id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "public_b" {
  subnet_id      = aws_subnet.public_b.id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "private_a" {
  subnet_id      = aws_subnet.private_a.id
  route_table_id = aws_route_table.private_a.id
}

resource "aws_route_table_association" "private_b" {
  subnet_id      = aws_subnet.private_b.id
  route_table_id = aws_route_table.private_b.id
}

############################################
# NETWORK ACLs (PUBLIC)
############################################
resource "aws_network_acl" "public_nacl" {
  vpc_id = aws_vpc.project_vpc.id

  tags = {
    Name = "PublicNACL"
  }
}

resource "aws_network_acl_rule" "public_inbound" {
  network_acl_id = aws_network_acl.public_nacl.id
  rule_number    = 100
  egress         = false
  protocol       = "-1"
  rule_action    = "allow"
  cidr_block     = "0.0.0.0/0"
}

resource "aws_network_acl_rule" "public_outbound" {
  network_acl_id = aws_network_acl.public_nacl.id
  rule_number    = 200
  egress         = true
  protocol       = "-1"
  rule_action    = "allow"
  cidr_block     = "0.0.0.0/0"
}

# PublicSubnetA only (matches CloudFormation)
resource "aws_network_acl_association" "public_a_assoc" {
  subnet_id      = aws_subnet.public_a.id
  network_acl_id = aws_network_acl.public_nacl.id
}

############################################
# NETWORK ACLs (PRIVATE)
############################################
resource "aws_network_acl" "private_nacl" {
  vpc_id = aws_vpc.project_vpc.id

  tags = {
    Name = "PrivateNACL"
  }
}

############################################
# NETWORK ACL ASSOCIATIONS (PRIVATE)
############################################

resource "aws_network_acl_association" "private_a_assoc" {
  subnet_id      = aws_subnet.private_a.id
  network_acl_id = aws_network_acl.private_nacl.id
}

resource "aws_network_acl_association" "private_b_assoc" {
  subnet_id      = aws_subnet.private_b.id
  network_acl_id = aws_network_acl.private_nacl.id
}


############################################
# SECURITY GROUPS
############################################
resource "aws_security_group" "alb_sg" {
  vpc_id = aws_vpc.project_vpc.id
  name   = "ALBSecurityGroup"

  ingress {
    protocol    = "tcp"
    from_port   = 80
    to_port     = 80
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "ecs_sg" {
  vpc_id = aws_vpc.project_vpc.id
  name   = "ECSSecurityGroup"

  ingress {
    protocol                 = "tcp"
    from_port                = 80
    to_port                  = 80
    security_groups          = [aws_security_group.alb_sg.id]
  }
}

resource "aws_security_group" "rds_sg" {
  name        = "rds-sg"
  description = "Allow Grafana to access RDS"
  vpc_id      = aws_vpc.project_vpc.id
}


############################################
# IAM ROLE FOR ECS TASK
############################################
resource "aws_iam_role" "ecs_task_role" {
  name = "WebServerIAMRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_execution" {
  role       = aws_iam_role.ecs_task_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role_policy_attachment" "ecr_readonly" {
  role       = aws_iam_role.ecs_task_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
}

############################################
# ECS CLUSTER
############################################
resource "aws_ecs_cluster" "web_cluster" {
  name = "WebServerCluster"
}

############################################
# APPLICATION LOAD BALANCER
############################################
resource "aws_lb" "web_alb" {
  name               = "WebServer-alb"
  load_balancer_type = "application"
  internal           = false
  security_groups    = [aws_security_group.alb_sg.id]
  subnets            = [
    aws_subnet.public_a.id,
    aws_subnet.public_b.id
  ]
}

############################################
# TARGET GROUP
############################################
resource "aws_lb_target_group" "web_tg" {
  name        = "web-target-group"
  port        = 80
  protocol    = "HTTP"
  target_type = "ip"
  vpc_id      = aws_vpc.project_vpc.id

  health_check {
    path = "/health"
    port = "traffic-port"
  }
}

############################################
# LISTENER
############################################
resource "aws_lb_listener" "web_listener" {
  load_balancer_arn = aws_lb.web_alb.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.web_tg.arn
  }
}

############################################
# ECS TASK DEFINITION
############################################
resource "aws_ecs_task_definition" "web_task" {
  family                   = "WebServerTask"
  cpu                      = "512"
  memory                   = "1024"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  execution_role_arn       = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name      = "webServer"
      image     = "108271871935.dkr.ecr.ca-central-1.amazonaws.com/fraud-detection-repo:latest"
      essential = true

      portMappings = [{
        containerPort = 80
      }]
    }
  ])
}

############################################
# ECS SERVICE
############################################
resource "aws_ecs_service" "web_service" {
  name            = "WebServerService"
  cluster         = aws_ecs_cluster.web_cluster.id
  launch_type     = "FARGATE"
  desired_count   = 2
  task_definition = aws_ecs_task_definition.web_task.arn

  load_balancer {
    container_name = "webServer"
    container_port = 80
    target_group_arn = aws_lb_target_group.web_tg.arn
  }

  network_configuration {
    subnets         = [aws_subnet.public_a.id, aws_subnet.public_b.id]
    security_groups = [aws_security_group.ecs_sg.id]
    assign_public_ip = true
  }

  depends_on = [
    aws_lb_listener.web_listener
  ]
}


# -------------------------------------
# Redshift IAM Role - to read from S3
# ------------------------------------


resource "aws_iam_role" "redshift_role" {
  name = "RedshiftCopyRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "redshift.amazonaws.com"
      }
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "redshift_s3_read" {
  role       = aws_iam_role.redshift_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"
}

resource "aws_redshift_cluster_iam_roles" "analytics_roles" {
  cluster_identifier = aws_redshift_cluster.analytics_cluster.id
  iam_role_arns      = [aws_iam_role.redshift_role.arn]
}

# -----------------------------
# Redshift
# -----------------------------
resource "aws_redshift_subnet_group" "redshift_subnet_group" {
  name       = "redshift-subnet-group"
  subnet_ids = [
    aws_subnet.public_a.id,
    aws_subnet.public_b.id
  ]
}

resource "aws_redshift_cluster" "analytics_cluster" {
  cluster_identifier       = "analytics-cluster"
  node_type                = "ra3.xlplus"
  number_of_nodes          = 1
  master_username          = var.redshift_username
  master_password          = var.redshift_password
  cluster_subnet_group_name = aws_redshift_subnet_group.redshift_subnet_group.name
  vpc_security_group_ids = [aws_security_group.redshift_sg.id]

  # Explicitly set this
  publicly_accessible       = true 
  encrypted                 = true

  # Important for dev/test: skip snapshot on destroy
  skip_final_snapshot       = true

  # If you want AutoFailover, set it here at creation time
  availability_zone_relocation_enabled = true
}


# -----------------------------
# Grafana IAM Role
# -----------------------------

resource "aws_iam_role" "grafana_role" {
  name = "FraudLabGrafanaRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "grafana.amazonaws.com"
      }
      Action = "sts:AssumeRole"
    }]
  })
}

# Attach Grafana administrator policy
resource "aws_iam_role_policy_attachment" "grafana_admin_attachment" {
  role       = aws_iam_role.grafana_role.name
  policy_arn = "arn:aws:iam::aws:policy/AWSGrafanaAccountAdministrator"
}

resource "aws_iam_role_policy_attachment" "grafana_redshift_read" {
  role       = aws_iam_role.grafana_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonRedshiftReadOnlyAccess"
}

resource "aws_iam_policy" "grafana_redshift_access" {
  name   = "GrafanaRedshiftAccess"
  policy = var.grafana_redshift_policy_json
}


resource "aws_iam_role_policy_attachment" "grafana_redshift_access" {
  role       = aws_iam_role.grafana_role.name
  policy_arn = aws_iam_policy.grafana_redshift_access.arn
}

# -----------------------------
# Grafana Security Group
# -----------------------------
resource "aws_security_group" "grafana_sg" {
  name        = "grafana-sg"
  description = "Allow Grafana to access Redshift"
  vpc_id      = aws_vpc.project_vpc.id

  # outbound rules so Grafana can reach Redshift
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}


resource "aws_security_group" "redshift_sg" {
  name        = "redshift-sg"
  description = "Allow Grafana to access Redshift"
  vpc_id      = aws_vpc.project_vpc.id
}

# -----------------------------
# Allow Grafana → Redshift
# -----------------------------
resource "aws_security_group_rule" "allow_grafana_to_redshift" {
  type                     = "ingress"
  from_port                = 5439
  to_port                  = 5439
  protocol                 = "tcp"
  source_security_group_id = aws_security_group.grafana_sg.id
  security_group_id        = aws_security_group.redshift_sg.id
}

resource "aws_security_group_rule" "allow_grafana_to_rds" {
  type                     = "ingress"
  from_port                = 5432
  to_port                  = 5432
  protocol                 = "tcp"
  source_security_group_id = aws_security_group.grafana_sg.id
  security_group_id        = aws_security_group.rds_sg.id
}

resource "aws_security_group_rule" "allow_cloudshell_to_redshift" {
  type              = "ingress"
  from_port         = 5439
  to_port           = 5439
  protocol          = "tcp"
  cidr_blocks       = ["35.183.245.80/32"]   # or replace with your workstation’s public IP
  security_group_id = aws_security_group.redshift_sg.id
}

