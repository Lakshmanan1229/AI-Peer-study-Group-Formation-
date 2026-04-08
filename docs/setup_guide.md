# Setup Guide

## Prerequisites

Ensure the following tools are installed on your development machine:

| Tool | Version | Purpose |
|------|---------|---------|
| **Python** | 3.11+ | Backend runtime |
| **Node.js** | 20+ | Frontend build toolchain |
| **npm** | 10+ | Frontend package manager (comes with Node.js) |
| **Docker** | 24+ | Containerization |
| **Docker Compose** | v2+ | Multi-container orchestration |
| **PostgreSQL** | 16+ | Database (with pgvector extension) |
| **Redis** | 7+ | Caching and task broker |
| **Git** | 2.40+ | Version control |
| **Terraform** | 1.6+ | Infrastructure as code (for cloud deployment) |
| **AWS CLI** | 2+ | Cloud deployment (for cloud deployment) |

### Quick Install (Ubuntu/Debian)

```bash
# Python 3.11
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip

# Node.js 20 (via NodeSource)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Docker
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER

# PostgreSQL 16 + pgvector
sudo apt install postgresql-16 postgresql-16-pgvector

# Redis
sudo apt install redis-server
```

### Quick Install (macOS)

```bash
# Using Homebrew
brew install python@3.11 node@20 docker docker-compose
brew install postgresql@16 redis

# pgvector extension
brew install pgvector
```

---

## Local Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/AI-Peer-study-Group-Formation-.git
cd AI-Peer-study-Group-Formation-
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create a virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
```

Edit `.env` with your local configuration:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/peergroup
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-super-secret-key-change-in-production-minimum-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
SENTENCE_TRANSFORMER_MODEL=all-MiniLM-L6-v2
ENVIRONMENT=development
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

### 3. Database Setup

```bash
# Start PostgreSQL (if not running)
sudo systemctl start postgresql

# Create the database and enable pgvector
sudo -u postgres psql -c "CREATE DATABASE peergroup;"
sudo -u postgres psql -d peergroup -c "CREATE EXTENSION IF NOT EXISTS vector;"

# Run database migrations
cd backend
alembic upgrade head
```

### 4. Seed Data (Optional)

Generate synthetic student data for development:

```bash
# From project root
make seed

# Or manually
cd data_pipeline
pip install -r requirements.txt
python generators/synthetic_data.py
```

### 5. Start the Backend

```bash
cd backend

# Using Make
make dev

# Or directly with uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Swagger Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 6. Frontend Setup

```bash
# Navigate to frontend directory (from project root)
cd frontend

# Install dependencies
npm ci

# Start development server
npm run dev
```

The frontend will be available at http://localhost:5173.

### 7. Start Redis

```bash
# Start Redis server
sudo systemctl start redis

# Verify Redis is running
redis-cli ping
# Expected output: PONG
```

### 8. Verify the Setup

```bash
# Check API health
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","environment":"development","version":"1.0.0"}
```

---

## Docker Setup

The recommended way to run the full stack locally is with Docker Compose.

### 1. Build and Start All Services

```bash
# From project root
make docker-up

# Or directly with Docker Compose
cd infrastructure
docker compose up --build -d
```

This starts four services:

| Service | Port | Description |
|---------|------|-------------|
| **postgres** | 5432 | PostgreSQL 16 with pgvector extension |
| **redis** | 6379 | Redis 7 for caching and Celery broker |
| **backend** | 8000 | FastAPI backend application |
| **frontend** | 3000 | Nginx serving the React SPA |

### 2. Verify Services

```bash
# Check all containers are running
docker compose ps

# Check backend health
curl http://localhost:8000/health

# Check frontend
curl -I http://localhost:3000
```

### 3. View Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend
docker compose logs -f postgres
```

### 4. Run Migrations in Docker

```bash
docker compose exec backend alembic upgrade head
```

### 5. Stop Services

```bash
make docker-down

# Or directly
cd infrastructure
docker compose down

# Remove volumes (caution: deletes database data)
docker compose down -v
```

---

## Running Tests

### Backend Tests

```bash
cd backend

# Run all tests with coverage
make test

# Or directly with pytest
pytest tests/ -v --cov=app --cov-report=term-missing

# Run specific test file
pytest tests/test_auth.py -v

# Run tests matching a pattern
pytest tests/ -k "test_login" -v
```

### Linting

```bash
cd backend

# Run all linters
make lint

# Or individually
black --check app/ tests/
isort --check-only app/ tests/
flake8 app/ tests/ --max-line-length=120 --ignore=E501,W503

# Auto-fix formatting
black app/ tests/
isort app/ tests/
```

### Frontend

```bash
cd frontend

# Type checking
npx tsc --noEmit

# Build (validates compilation)
npm run build

# Lint
npm run lint
```

---

## Cloud Deployment (AWS)

### Prerequisites

1. **AWS Account** with appropriate IAM permissions
2. **AWS CLI** configured with credentials
3. **Terraform** installed (v1.6+)
4. **GitHub repository** with Actions enabled

### 1. Configure AWS CLI

```bash
aws configure
# Enter your AWS Access Key ID, Secret Access Key, and region (ap-south-1)
```

### 2. Create Terraform State Backend

```bash
# Create S3 bucket for Terraform state
aws s3api create-bucket \
  --bucket smvec-terraform-state \
  --region ap-south-1 \
  --create-bucket-configuration LocationConstraint=ap-south-1

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket smvec-terraform-state \
  --versioning-configuration Status=Enabled

# Create DynamoDB table for state locking
aws dynamodb create-table \
  --table-name terraform-locks \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region ap-south-1
```

### 3. Initialize and Apply Terraform

```bash
cd infrastructure/terraform

# Initialize Terraform
terraform init

# Review the execution plan
terraform plan -var="db_password=YOUR_SECURE_PASSWORD"

# Apply infrastructure changes
terraform apply -var="db_password=YOUR_SECURE_PASSWORD"
```

This provisions:
- VPC with public and private subnets across 2 availability zones
- RDS PostgreSQL 15 (Multi-AZ) with pgvector extension
- ElastiCache Redis 7
- ECS Fargate cluster with Application Load Balancer
- ECR repository for Docker images
- S3 buckets (frontend hosting + data lake)
- CloudFront CDN distribution

### 4. Configure GitHub Secrets

Add the following secrets to your GitHub repository (Settings → Secrets and variables → Actions):

| Secret | Description |
|--------|-------------|
| `AWS_ROLE_ARN` | IAM role ARN for GitHub Actions OIDC authentication |
| `API_BASE_URL` | Production API URL (e.g., `https://api.smvec-peerstudy.example.com`) |
| `CLOUDFRONT_DISTRIBUTION_ID` | CloudFront distribution ID for cache invalidation |

### 5. Set Up OIDC for GitHub Actions

```bash
# Create an OIDC identity provider in AWS IAM
aws iam create-open-id-connect-provider \
  --url https://token.actions.githubusercontent.com \
  --client-id-list sts.amazonaws.com \
  --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1

# Create an IAM role with the trust policy for your repository
# (See AWS docs for the trust policy JSON)
```

### 6. Deploy

Push to the `main` branch to trigger the deployment pipeline:

```bash
git checkout main
git merge develop
git push origin main
```

The GitHub Actions workflow will:
1. Run all tests (backend + frontend + lint)
2. Build and push the backend Docker image to ECR
3. Deploy the backend to ECS Fargate
4. Build the frontend and sync to S3
5. Invalidate the CloudFront cache

---

## Environment Variables Reference

### Backend

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes | — | PostgreSQL connection string (`postgresql+asyncpg://...`) |
| `REDIS_URL` | Yes | — | Redis connection string (`redis://...`) |
| `SECRET_KEY` | Yes | — | JWT signing key (minimum 32 characters) |
| `ALGORITHM` | No | `HS256` | JWT signing algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | `30` | Access token TTL in minutes |
| `REFRESH_TOKEN_EXPIRE_DAYS` | No | `7` | Refresh token TTL in days |
| `SENTENCE_TRANSFORMER_MODEL` | No | `all-MiniLM-L6-v2` | Sentence-transformers model for goal embeddings |
| `ENVIRONMENT` | No | `development` | Runtime environment (`development`, `testing`, `production`) |
| `ALLOWED_ORIGINS` | No | `*` | Comma-separated CORS allowed origins |
| `AWS_ACCESS_KEY_ID` | No | — | AWS access key (for S3 data lake) |
| `AWS_SECRET_ACCESS_KEY` | No | — | AWS secret key (for S3 data lake) |
| `AWS_REGION` | No | `ap-south-1` | AWS region |
| `S3_BUCKET_NAME` | No | — | S3 bucket for data lake storage |

### Frontend

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `VITE_API_BASE_URL` | No | `http://localhost:8000` | Backend API base URL |

### Docker Compose (infrastructure/docker-compose.yml)

| Variable | Service | Default | Description |
|----------|---------|---------|-------------|
| `POSTGRES_DB` | postgres | `peergroup` | Database name |
| `POSTGRES_USER` | postgres | `postgres` | Database user |
| `POSTGRES_PASSWORD` | postgres | `postgres` | Database password |

---

## Troubleshooting

### Database Connection Errors

**Problem**: `sqlalchemy.exc.OperationalError: could not connect to server`

**Solution**:
```bash
# Ensure PostgreSQL is running
sudo systemctl status postgresql

# Check if the database exists
sudo -u postgres psql -l | grep peergroup

# Verify connection string in .env
# Format: postgresql+asyncpg://user:password@host:port/database
```

### pgvector Extension Not Found

**Problem**: `ERROR: extension "vector" is not available`

**Solution**:
```bash
# Install pgvector
sudo apt install postgresql-16-pgvector

# Or compile from source
cd /path/to/pgvector
make && sudo make install

# Enable the extension
sudo -u postgres psql -d peergroup -c "CREATE EXTENSION vector;"
```

### Redis Connection Refused

**Problem**: `redis.exceptions.ConnectionError: Connection refused`

**Solution**:
```bash
# Start Redis
sudo systemctl start redis

# Verify Redis is accessible
redis-cli ping
# Expected: PONG

# Check if port 6379 is in use
sudo lsof -i :6379
```

### Frontend Build Fails

**Problem**: `npm ci` or `npm run build` fails

**Solution**:
```bash
# Clear npm cache and node_modules
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build

# Ensure correct Node.js version
node --version  # Should be 20.x
```

### Sentence-Transformer Model Download

**Problem**: Model download fails or is slow on first startup

**Solution**:
```bash
# Pre-download the model
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# The model (~90MB) is cached in ~/.cache/huggingface/
```

### Docker Compose Issues

**Problem**: Containers fail to start or cannot communicate

**Solution**:
```bash
# Rebuild all images from scratch
docker compose build --no-cache

# Remove all containers, networks, and volumes
docker compose down -v

# Start fresh
docker compose up --build

# Check container logs for errors
docker compose logs backend
docker compose logs postgres
```

### Alembic Migration Errors

**Problem**: `alembic upgrade head` fails

**Solution**:
```bash
# Check current migration state
alembic current

# View migration history
alembic history

# If database is fresh, stamp the initial state
alembic stamp head

# Then re-run migrations
alembic downgrade base
alembic upgrade head
```

### Port Conflicts

**Problem**: `Address already in use` errors

**Solution**:
```bash
# Find the process using the port
sudo lsof -i :8000  # Backend
sudo lsof -i :5173  # Frontend dev server
sudo lsof -i :5432  # PostgreSQL
sudo lsof -i :6379  # Redis

# Stop the conflicting process
kill <PID>
```

### JWT Token Issues

**Problem**: `401 Unauthorized` on every request

**Solution**:
- Verify `SECRET_KEY` in `.env` is at least 32 characters
- Check that `ALGORITHM` is set to `HS256`
- Ensure the access token hasn't expired (30-minute default)
- Use the refresh token endpoint to get a new token pair

### ML Pipeline Errors

**Problem**: Group formation fails or produces poor results

**Solution**:
```bash
# Ensure sufficient students exist (minimum ~10 for meaningful clustering)
# Check that students have:
# - At least 1 skill assessment
# - At least 1 availability slot
# - Goals text set (for embeddings)

# Verify sentence-transformer model is loaded
python -c "from app.ml.nlp_goals import encode_goals; print('Model loaded successfully')"
```

---

## Makefile Commands Reference

Run `make help` to see all available commands:

| Command | Description |
|---------|-------------|
| `make dev` | Start FastAPI server with hot-reload |
| `make install` | Install Python backend dependencies |
| `make test` | Run pytest with coverage report |
| `make lint` | Run flake8, black, and isort checks |
| `make migrate` | Apply Alembic database migrations |
| `make seed` | Generate and load synthetic student data |
| `make docker-up` | Build and start all Docker services |
| `make docker-down` | Stop all Docker containers |
| `make frontend-install` | Install frontend npm dependencies |
| `make frontend-dev` | Start Vite development server |
| `make frontend-build` | Build React SPA for production |
