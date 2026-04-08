# System Architecture

## Overview

The AI Peer Study Group Formation System is an intelligent, data-driven platform that automatically forms optimally matched peer study groups at Sri Manakula Vinayagar Engineering College (SMVEC), Puducherry. It uses machine learning algorithms including KMeans/DBSCAN hybrid clustering, sentence-transformer embeddings, and multi-objective optimization to match students based on skills, goals, schedules, and learning pace.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                            CLIENTS                                      │
│                                                                         │
│    ┌──────────────┐    ┌──────────────┐    ┌──────────────────┐        │
│    │  Web Browser  │    │  Mobile App  │    │  Admin Console   │        │
│    └──────┬───────┘    └──────┬───────┘    └────────┬─────────┘        │
└───────────┼───────────────────┼─────────────────────┼──────────────────┘
            │                   │                     │
            ▼                   ▼                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        CDN / LOAD BALANCER                              │
│                                                                         │
│    ┌──────────────────────┐    ┌───────────────────────────────┐       │
│    │  CloudFront (CDN)    │    │  Application Load Balancer    │       │
│    │  Static Assets (S3)  │    │  HTTPS Termination            │       │
│    └──────────┬───────────┘    └───────────────┬───────────────┘       │
└───────────────┼────────────────────────────────┼───────────────────────┘
                │                                │
                ▼                                ▼
┌──────────────────────────┐    ┌──────────────────────────────────────┐
│      FRONTEND             │    │           BACKEND                     │
│                           │    │                                       │
│  React 18 + TypeScript    │    │  FastAPI (Python 3.11)                │
│  Vite Build Tool          │    │  ┌─────────────────────────────┐     │
│  Tailwind CSS             │    │  │  API Layer (/api/v1/)        │     │
│  Zustand State Mgmt       │    │  │  ├── Auth Router             │     │
│  React Router v6          │    │  │  ├── Students Router         │     │
│  Recharts Visualizations  │    │  │  ├── Groups Router           │     │
│  Axios HTTP Client        │    │  │  ├── Feedback Router         │     │
│                           │    │  │  ├── Recommendations Router  │     │
│  Pages:                   │    │  │  └── Admin Router            │     │
│  ├── Login / Register     │    │  └─────────────────────────────┘     │
│  ├── Dashboard            │    │  ┌─────────────────────────────┐     │
│  ├── Group View           │    │  │  Service Layer               │     │
│  ├── Schedule Manager     │    │  │  ├── AuthService             │     │
│  ├── Feedback             │    │  │  ├── StudentService          │     │
│  ├── Recommendations      │    │  │  ├── GroupService            │     │
│  ├── Statistics           │    │  │  └── RecommendationService   │     │
│  └── Admin Dashboard      │    │  └─────────────────────────────┘     │
│                           │    │  ┌─────────────────────────────┐     │
└──────────────────────────┘    │  │  ML Pipeline                  │     │
                                 │  │  ├── Feature Engineering      │     │
                                 │  │  ├── KMeans + DBSCAN          │     │
                                 │  │  ├── Group Optimizer          │     │
                                 │  │  ├── NLP Goal Embeddings      │     │
                                 │  │  └── Recommender Engine       │     │
                                 │  └─────────────────────────────┘     │
                                 └──────────┬──────────┬────────────────┘
                                            │          │
                              ┌─────────────┘          └──────────────┐
                              ▼                                       ▼
                 ┌──────────────────────┐              ┌──────────────────┐
                 │  PostgreSQL 16       │              │  Redis 7          │
                 │  + pgvector          │              │                   │
                 │                      │              │  Session Cache    │
                 │  Students            │              │  Rate Limiting    │
                 │  Skills              │              │  Celery Broker    │
                 │  Availability        │              │  Pub/Sub          │
                 │  Study Groups        │              │                   │
                 │  Memberships         │              └──────────────────┘
                 │  Sessions            │
                 │  Feedbacks           │
                 │  Vector Embeddings   │
                 └──────────────────────┘
```

## Component Architecture

### Frontend (React + TypeScript)

The frontend is a single-page application built with React 18 and TypeScript, bundled with Vite for fast development and optimized production builds.

| Layer | Technology | Purpose |
|-------|-----------|---------|
| UI Framework | React 18 | Component-based UI rendering |
| Type Safety | TypeScript | Static type checking |
| Styling | Tailwind CSS | Utility-first CSS framework |
| State Management | Zustand | Lightweight global state |
| Routing | React Router v6 | Client-side navigation |
| HTTP Client | Axios | API communication with interceptors |
| Charts | Recharts | Data visualization (skill radar, analytics) |
| Icons | Lucide React | Consistent icon set |
| Build Tool | Vite | Fast HMR and optimized bundles |

**Key Pages:**
- **LoginPage / RegisterPage** — JWT-based authentication flow
- **DashboardPage** — Student overview with group info, upcoming sessions, skill summary
- **GroupPage** — Active group details, member cards, health score gauge, skill exchange map
- **SchedulePage** — Weekly availability grid editor (morning/afternoon/evening × 7 days)
- **FeedbackPage** — Peer feedback submission with rating and helpfulness scores
- **RecommendationsPage** — AI-curated learning resources and mentor suggestions
- **StatsPage** — Personal analytics and progress tracking
- **AdminPage** — System-wide analytics, trigger grouping, manage students and groups

### Backend (FastAPI)

The backend follows a layered architecture with clear separation of concerns:

```
Request → Router → Service → Repository/ORM → Database
                     ↕
                  ML Pipeline
```

**Layers:**
1. **Routers** (`app/routers/`) — HTTP endpoint definitions, request validation, response serialization
2. **Schemas** (`app/schemas/`) — Pydantic models for request/response validation
3. **Services** (`app/services/`) — Business logic, orchestration between repositories and ML modules
4. **Models** (`app/models/`) — SQLAlchemy ORM models mapped to PostgreSQL tables
5. **ML Modules** (`app/ml/`) — Machine learning algorithms for clustering, recommendations, NLP
6. **Middleware** (`app/middleware/`) — JWT authentication, CORS, error handling
7. **Utils** (`app/utils/`) — Password hashing, token generation, helper functions

**Key Configuration:**
- Async-first design using `asyncpg` for PostgreSQL and `aioredis` for Redis
- Automatic OpenAPI documentation at `/docs` (Swagger) and `/redoc`
- Alembic for database migrations with pgvector support

### ML Pipeline

The ML pipeline is the core intelligence of the system, responsible for forming optimal study groups.

```
┌─────────────┐    ┌──────────────────┐    ┌──────────────────┐    ┌──────────────┐
│   Student    │    │     Feature      │    │   Clustering     │    │    Group      │
│   Profiles   │───▶│   Engineering    │───▶│   (Hybrid)       │───▶│  Optimizer    │
│              │    │                  │    │                  │    │              │
│ • Skills     │    │ • Normalize      │    │ • PCA (20 dims)  │    │ • Skill-gap  │
│ • Goals      │    │ • Encode goals   │    │ • KMeans (k=8)   │    │   balancing  │
│ • Schedule   │    │ • Build matrix   │    │ • DBSCAN refine  │    │ • Schedule   │
│ • CGPA       │    │ • Scale features │    │ • Outlier assign │    │   overlap    │
│ • Pace       │    │                  │    │                  │    │ • Goal sim.  │
└─────────────┘    └──────────────────┘    └──────────────────┘    │ • Health     │
                                                                    │   scoring    │
                                                                    └──────┬───────┘
                                                                           │
                                                                           ▼
                                                                    ┌──────────────┐
                                                                    │  Formed      │
                                                                    │  Study       │
                                                                    │  Groups      │
                                                                    └──────────────┘
```

**Algorithms:**

1. **Feature Engineering** (`feature_engineering.py`)
   - Combines skill self-ratings, CGPA, learning pace (encoded), schedule availability vectors, and goal embeddings (384-dimensional vectors from `all-MiniLM-L6-v2`)
   - Normalizes all features to [0, 1] range for consistent clustering

2. **Hybrid Clustering** (`clustering.py`)
   - **Stage 1 — PCA:** Reduces feature dimensionality to 20 principal components
   - **Stage 2 — KMeans:** Creates k=8 initial cluster archetypes
   - **Stage 3 — DBSCAN:** Refines clusters (eps=0.5, min_samples=3) to detect density-based groupings and outliers
   - **Stage 4 — Outlier Reassignment:** Students labeled as outliers (label=-1) by DBSCAN are reassigned to their nearest KMeans centroid

3. **Group Optimizer** (`group_optimizer.py`)
   - Balances skill gaps within groups (ensures mix of beginner/advanced per subject)
   - Maximizes schedule overlap (≥1 common free slot per week)
   - Optimizes goal similarity using cosine similarity on pgvector embeddings
   - Computes group health scores (0-100) based on complementary score, schedule overlap count, and goal similarity

4. **NLP Goals Processing** (`nlp_goals.py`)
   - Uses `sentence-transformers` model `all-MiniLM-L6-v2` to encode student goals into 384-dimensional vectors
   - Stores vectors in PostgreSQL using the pgvector extension for efficient cosine similarity search
   - Enables semantic matching of students with similar learning objectives

5. **Recommender Engine** (`recommender.py`)
   - **Resources:** Content-based filtering from a curated catalog of 30+ learning resources (books, videos, articles, courses), filtered by subject, difficulty level, and student learning needs
   - **Mentors:** Collaborative filtering to find peer mentors with complementary skill strengths

### Data Pipeline

The data pipeline handles synthetic data generation for development/testing and ETL workflows for production data ingestion.

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Data Source  │    │   Extract    │    │  Transform   │    │    Load      │
│              │    │              │    │              │    │              │
│ • CSV Files  │───▶│ • Read CSV   │───▶│ • Clean data │───▶│ • PostgreSQL │
│ • APIs       │    │ • API calls  │    │ • Standardize│    │ • pgvector   │
│ • Faker      │    │ • DB queries │    │ • Embeddings │    │ • S3 (lake)  │
└──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
```

- **Synthetic Data Generator** (`generators/synthetic_data.py`) — Uses Faker library to create realistic student profiles for testing
- **ETL Pipeline** (`etl/`) — Extract from multiple sources, transform with standardization and embedding generation, load into PostgreSQL and pgvector

## Database Schema

### Entity-Relationship Diagram

```
┌─────────────────┐       ┌────────────────────┐       ┌─────────────────────┐
│    students      │       │  skill_assessments  │       │  availability_slots  │
├─────────────────┤       ├────────────────────┤       ├─────────────────────┤
│ id (UUID, PK)   │──┐    │ id (INT, PK)       │       │ id (INT, PK)        │
│ email (UNIQUE)  │  │    │ student_id (FK)  ──┼───┐   │ student_id (FK)  ───┼──┐
│ hashed_password  │  │    │ subject            │   │   │ day_of_week         │  │
│ full_name       │  │    │ self_rating        │   │   │ slot (ENUM)         │  │
│ department      │  │    │ peer_rating        │   │   │ is_available        │  │
│ year            │  │    │ grade_points       │   │   └─────────────────────┘  │
│ cgpa            │  │    │ created_at         │   │                            │
│ learning_pace   │  │    │ updated_at         │   │                            │
│ role            │  │    └────────────────────┘   │                            │
│ is_active       │  │                              │                            │
│ goals           │  └──────────────────────────────┴────────────────────────────┘
│ goal_embedding  │                                        │
│   (vector 384)  │                                        │
│ created_at      │──────────────────────────────┐         │
│ updated_at      │                              │         │
└─────────────────┘                              │         │
        │                                        │         │
        │  ┌──────────────────────┐              │         │
        │  │   study_groups       │              │         │
        │  ├──────────────────────┤              │         │
        │  │ id (UUID, PK)       │              │         │
        │  │ name                │              │         │
        │  │ department          │              │         │
        │  │ status (ENUM)      │              │         │
        │  │ max_size           │              │         │
        │  │ complementary_score │              │         │
        │  │ schedule_overlap    │              │         │
        │  │ goal_similarity     │              │         │
        │  │ created_at          │              │         │
        │  │ updated_at          │              │         │
        │  └─────────┬──────────┘              │         │
        │            │                          │         │
        │            ▼                          │         │
        │  ┌──────────────────────┐            │         │
        │  │  group_memberships   │            │         │
        │  ├──────────────────────┤            │         │
        ├─▶│ id (INT, PK)        │            │         │
        │  │ group_id (FK)       │            │         │
        │  │ student_id (FK)     │            │         │
        │  │ role (ENUM)         │            │         │
        │  │ joined_at           │            │         │
        │  │ left_at             │            │         │
        │  └──────────────────────┘            │         │
        │                                      │         │
        │  ┌──────────────────────┐            │         │
        │  │   group_sessions     │            │         │
        │  ├──────────────────────┤            │         │
        │  │ id (UUID, PK)       │            │         │
        │  │ group_id (FK)       │────────────┘         │
        │  │ scheduled_at        │                       │
        │  │ duration_minutes    │                       │
        │  │ location            │                       │
        │  │ session_type (ENUM) │                       │
        │  │ notes               │                       │
        │  │ attendance (JSONB)  │                       │
        │  │ created_by (FK)  ───┼───────────────────────┘
        │  │ created_at          │
        │  └──────────────────────┘
        │
        │  ┌──────────────────────┐
        │  │   peer_feedbacks     │
        │  ├──────────────────────┤
        └─▶│ id (UUID, PK)       │
           │ reviewer_id (FK)    │
           │ reviewee_id (FK)    │
           │ group_id (FK)       │
           │ session_id (FK)     │
           │ rating              │
           │ helpfulness_score   │
           │ comment             │
           │ is_anonymous        │
           │ created_at          │
           └──────────────────────┘
```

### Table Descriptions

| Table | Records | Purpose |
|-------|---------|---------|
| **students** | One per registered user | Core user profile with academic info, learning preferences, and goal embeddings (pgvector 384-dim) |
| **skill_assessments** | Many per student | Subject-level skill ratings (self, peer, grade) used as features for clustering |
| **availability_slots** | Up to 21 per student | Weekly availability grid (7 days × 3 slots: morning, afternoon, evening) |
| **study_groups** | One per formed group | Group metadata including ML-computed quality scores |
| **group_memberships** | Links students to groups | Many-to-many with role (member/leader) and temporal tracking |
| **group_sessions** | Many per group | Scheduled study sessions with attendance tracking (JSONB) |
| **peer_feedbacks** | Many per group/session | Peer review data used for group health monitoring and skill rating updates |

### Key Relationships
- **students → skill_assessments**: One-to-many (CASCADE delete)
- **students → availability_slots**: One-to-many (CASCADE delete)
- **students ↔ study_groups**: Many-to-many via group_memberships
- **study_groups → group_sessions**: One-to-many (CASCADE delete)
- **students → peer_feedbacks**: One-to-many as both reviewer and reviewee
- **group_sessions → peer_feedbacks**: One-to-many (SET NULL on delete)

## API Design

### Principles
- **RESTful**: Resource-oriented URLs with standard HTTP methods
- **Versioned**: All endpoints under `/api/v1/` prefix for backward compatibility
- **Authenticated**: JWT Bearer tokens (access: 30 min, refresh: 7 days)
- **Validated**: Pydantic schemas for request/response validation with automatic OpenAPI generation
- **Async**: Full async/await support with `asyncpg` and `aioredis`

### Router Organization
| Router | Prefix | Auth | Description |
|--------|--------|------|-------------|
| auth | `/api/v1/auth` | Public | Registration, login, token refresh |
| students | `/api/v1/students` | JWT | Student profile and skill management |
| groups | `/api/v1/groups` | JWT | Group viewing, sessions, health |
| feedback | `/api/v1/feedback` | JWT | Peer feedback submission and reports |
| recommendations | `/api/v1/recommendations` | JWT | AI-powered resource and mentor suggestions |
| admin | `/api/v1/admin` | Admin JWT | System administration and analytics |

### Authentication Flow
```
┌──────────┐                     ┌──────────┐                    ┌──────────┐
│  Client   │                     │  Backend  │                    │   DB     │
└────┬─────┘                     └────┬─────┘                    └────┬─────┘
     │  POST /auth/register            │                               │
     │────────────────────────────────▶│  Hash password (bcrypt)       │
     │                                 │──────────────────────────────▶│
     │                                 │  Store student record         │
     │◀────────────────────────────────│                               │
     │  { access_token, refresh_token } │                               │
     │                                 │                               │
     │  GET /students/me               │                               │
     │  Authorization: Bearer <token>  │                               │
     │────────────────────────────────▶│  Verify JWT signature         │
     │                                 │  Extract user_id from claims  │
     │                                 │──────────────────────────────▶│
     │                                 │  Fetch student profile         │
     │◀────────────────────────────────│                               │
     │  { student profile }            │                               │
     │                                 │                               │
     │  POST /auth/refresh             │                               │
     │  { refresh_token }              │                               │
     │────────────────────────────────▶│  Verify refresh token         │
     │                                 │  Issue new token pair          │
     │◀────────────────────────────────│                               │
     │  { new access_token,            │                               │
     │    new refresh_token }          │                               │
```

## Security Architecture

### Authentication & Authorization
- **Password Hashing**: bcrypt with automatic salt generation
- **JWT Tokens**: Signed with HS256 algorithm using a 256-bit secret key
  - Access tokens expire in 30 minutes
  - Refresh tokens expire in 7 days
- **Role-Based Access Control (RBAC)**: Three roles — `student`, `faculty`, `admin`
  - Student endpoints require valid JWT
  - Admin endpoints require JWT with `admin` role claim
  - Public endpoints (auth, health) require no authentication

### Transport Security
- **HTTPS**: Enforced via ALB with ACM certificate
- **CORS**: Configured allowed origins (frontend domain only in production)
- **HSTS**: Strict Transport Security headers via CloudFront

### Data Security
- **Database Encryption**: RDS encryption at rest with AWS KMS
- **S3 Encryption**: Server-side encryption (SSE-KMS) for data lake bucket
- **Network Isolation**: RDS and ElastiCache in private subnets only
- **Security Groups**: Least-privilege access (ECS → RDS:5432, ECS → Redis:6379)
- **Secrets Management**: Environment variables via ECS task definitions, GitHub Secrets for CI/CD

## Infrastructure Architecture

### AWS Cloud Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                         VPC (10.0.0.0/16)                            │
│                                                                      │
│  ┌─────────────────────────────┐  ┌─────────────────────────────┐   │
│  │   Public Subnet (AZ-1a)     │  │   Public Subnet (AZ-1b)     │   │
│  │   10.0.1.0/24               │  │   10.0.2.0/24               │   │
│  │                              │  │                              │   │
│  │  ┌────────────────────────┐ │  │  ┌────────────────────────┐ │   │
│  │  │  ALB (Application     │ │  │  │  NAT Gateway           │ │   │
│  │  │  Load Balancer)       │ │  │  │                        │ │   │
│  │  └────────────────────────┘ │  │  └────────────────────────┘ │   │
│  └─────────────────────────────┘  └─────────────────────────────┘   │
│                                                                      │
│  ┌─────────────────────────────┐  ┌─────────────────────────────┐   │
│  │  Private Subnet (AZ-1a)     │  │  Private Subnet (AZ-1b)     │   │
│  │  10.0.3.0/24               │  │  10.0.4.0/24               │   │
│  │                              │  │                              │   │
│  │  ┌────────────────────────┐ │  │  ┌────────────────────────┐ │   │
│  │  │  ECS Fargate Tasks     │ │  │  │  ECS Fargate Tasks     │ │   │
│  │  │  (FastAPI Backend)     │ │  │  │  (FastAPI Backend)     │ │   │
│  │  └────────────────────────┘ │  │  └────────────────────────┘ │   │
│  │                              │  │                              │   │
│  │  ┌────────────────────────┐ │  │  ┌────────────────────────┐ │   │
│  │  │  RDS PostgreSQL 15     │ │  │  │  RDS (Standby)         │ │   │
│  │  │  + pgvector            │ │  │  │  Multi-AZ              │ │   │
│  │  └────────────────────────┘ │  │  └────────────────────────┘ │   │
│  │                              │  │                              │   │
│  │  ┌────────────────────────┐ │  │                              │   │
│  │  │  ElastiCache Redis 7   │ │  │                              │   │
│  │  └────────────────────────┘ │  │                              │   │
│  └─────────────────────────────┘  └─────────────────────────────┘   │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘

External:
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  CloudFront   │    │  S3 Buckets  │    │  ECR         │
│  (CDN)        │    │  • Frontend  │    │  (Container  │
│               │    │  • Data Lake │    │   Registry)  │
└──────────────┘    └──────────────┘    └──────────────┘
```

### Infrastructure Components

| Component | Service | Configuration |
|-----------|---------|---------------|
| **Compute** | ECS Fargate | Serverless containers, auto-scaling |
| **Database** | RDS PostgreSQL 15 | db.t3.medium, Multi-AZ, pgvector extension |
| **Cache** | ElastiCache Redis 7 | cache.t3.micro, session/rate-limit cache |
| **Storage** | S3 | Frontend static assets + data lake (encrypted) |
| **CDN** | CloudFront | Global edge caching, HTTPS, SPA routing |
| **Load Balancer** | ALB | HTTP/HTTPS, health checks on `/health` |
| **Container Registry** | ECR | Docker image storage for backend |
| **DNS** | Route 53 | Domain management (if configured) |
| **IaC** | Terraform | Full infrastructure as code |
| **CI/CD** | GitHub Actions | Automated testing, building, and deployment |

### Terraform State Management
- **Backend**: S3 bucket (`smvec-terraform-state`) with versioning
- **Lock**: DynamoDB table (`terraform-locks`) for concurrent access safety
- **Encryption**: Server-side encryption enabled

## Scalability Considerations

### Horizontal Scaling
- **ECS Fargate** auto-scales backend containers based on CPU/memory utilization
- **RDS Multi-AZ** provides automatic failover with zero data loss
- **CloudFront** distributes frontend assets across global edge locations
- **ALB** distributes traffic across multiple Fargate tasks

### Performance Optimizations
- **Redis Caching**: Frequently accessed data (group details, student profiles) cached in ElastiCache
- **pgvector Indexes**: HNSW or IVFFlat indexes on goal_embedding column for fast similarity search
- **Async I/O**: All database and Redis operations use async drivers (asyncpg, aioredis)
- **CDN Caching**: Static assets cached for 1 year (`max-age=31536000`), `index.html` always fresh

### ML Pipeline Scaling
- **Batch Processing**: Group formation runs as an admin-triggered batch job, not per-request
- **Celery Workers**: Long-running ML tasks offloaded to Celery workers with Redis broker
- **Model Caching**: Sentence-transformer model loaded once at startup and reused across requests
- **PCA Dimensionality Reduction**: Reduces feature space from 384+ dimensions to 20 before clustering

### Database Scaling
- **Connection Pooling**: SQLAlchemy async engine with configurable pool size
- **Read Replicas**: RDS supports read replicas for scaling read-heavy analytics queries
- **Storage Auto-Scaling**: RDS storage scales automatically from 20GB to 100GB
- **Backup Strategy**: Daily automated backups with 7-day retention
