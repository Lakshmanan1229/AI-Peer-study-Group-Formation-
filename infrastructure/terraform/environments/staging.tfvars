# =============================================================================
# Staging environment — smaller instances, single AZ, lower cost
# =============================================================================
# Usage: terraform plan -var-file=environments/staging.tfvars

project_name    = "smvec-peerstudy-staging"
environment     = "staging"
aws_region      = "ap-south-1"

# Networking
vpc_cidr            = "10.1.0.0/16"
availability_zones  = ["ap-south-1a"]

# Database
db_instance_class = "db.t3.micro"
db_name           = "peergroup_staging"

# Cache
redis_node_type = "cache.t3.micro"

# Compute
ecs_cpu       = 256
ecs_memory    = 512
desired_count = 1

# Domain
domain_name          = "staging.peerstudy.smvec.ac.in"
frontend_bucket_name = "smvec-peerstudy-frontend-staging"
