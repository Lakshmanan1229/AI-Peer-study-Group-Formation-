# =============================================================================
# Production environment — multi-AZ, larger instances
# =============================================================================
# Usage: terraform plan -var-file=environments/production.tfvars

project_name    = "smvec-peerstudy"
environment     = "production"
aws_region      = "ap-south-1"

# Networking
vpc_cidr            = "10.0.0.0/16"
availability_zones  = ["ap-south-1a", "ap-south-1b"]

# Database
db_instance_class = "db.t3.medium"
db_name           = "peergroup"

# Cache
redis_node_type = "cache.t3.small"

# Compute
ecs_cpu       = 512
ecs_memory    = 1024
desired_count = 2

# Domain
domain_name          = "peerstudy.smvec.ac.in"
frontend_bucket_name = "smvec-peerstudy-frontend"
