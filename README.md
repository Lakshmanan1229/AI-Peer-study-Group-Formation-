# AI Peer Study Group Formation System

> **SMVEC — Sri Manakula Vinayagar Engineering College, Puducherry**
> Intelligent, data-driven peer study group formation powered by AI/ML and modern web technologies.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18%2B-61DAFB.svg)](https://reactjs.org)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED.svg)](https://docker.com)

---

## Table of Contents

- [About](#about)
- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Setup Instructions](#setup-instructions)
  - [Local Development](#local-development)
  - [Docker](#docker)
  - [Cloud (AWS)](#cloud-aws)
- [API Documentation](#api-documentation)
- [Screenshots](#screenshots)
- [Contributing](#contributing)
- [License](#license)

---

## About

The **AI Peer Study Group Formation System** automates the creation of optimally matched student study groups at SMVEC. Instead of random or manual assignment, the platform uses semantic similarity of learning profiles, collaborative-filtering signals, and schedule-based constraints to pair students who will genuinely benefit from studying together.

Faculty can monitor group health metrics, reassign students, and export analytics reports — all through a responsive web dashboard.

---

## Features

1. **Semantic Profile Matching** — `sentence-transformers` encodes student learning profiles into dense vectors stored in pgvector; cosine-similarity search finds the most compatible peers in milliseconds.
2. **Schedule-Aware Grouping** — Overlap analysis across student timetables ensures every proposed group has at least one common free slot per week.
3. **Skill-Gap Balancing** — scikit-learn clustering distributes advanced and beginner students across groups to encourage peer teaching.
4. **Real-Time Notifications** — Redis Pub/Sub pushes WebSocket events to the React frontend when groups are formed, updated, or dissolved.
5. **Role-Based Access Control** — JWT-secured endpoints with three roles: `student`, `faculty`, and `admin`; Zustand manages client-side auth state.
6. **Interactive Dashboard** — Students view their current group, meeting schedule, shared resources, and progress metrics on a single-page React dashboard.
7. **Faculty Analytics Panel** — Aggregate statistics on group performance, attendance, and self-reported satisfaction scores with exportable CSV/PDF reports.
8. **Automated Re-Grouping** — Configurable cron job re-evaluates group fitness at the end of each academic module and proposes reassignments.
9. **Synthetic Data Generator** — Built-in data pipeline produces realistic student profiles for development and load-testing without touching real PII.
10. **Containerised & Cloud-Ready** — Full Docker Compose stack for local development; Terraform modules target AWS ECS + RDS + ElastiCache for production.
11. **REST + WebSocket API** — FastAPI exposes a versioned REST API (`/api/v1/`) and a `/ws` endpoint for live group-chat and notifications.
12. **OpenAPI / Swagger UI** — Auto-generated interactive API docs available at `/docs` and `/redoc` with no extra configuration.

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                              │
│                                                                  │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │          React 18  +  Zustand  +  Tailwind CSS          │   │
│   │   (Vite SPA — served from S3 / CloudFront in prod)      │   │
│   └───────────────────────┬─────────────────────────────────┘   │
│                           │  HTTPS / WSS                         │
└───────────────────────────┼──────────────────────────────────────┘
                            │
┌───────────────────────────▼──────────────────────────────────────┐
│                       API GATEWAY / ALB                          │
└───────────────────────────┬──────────────────────────────────────┘
                            │
┌───────────────────────────▼──────────────────────────────────────┐
│                    APPLICATION LAYER (ECS)                       │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              FastAPI  (Uvicorn / Gunicorn)               │   │
│  │  ┌────────────┐  ┌──────────────┐  ┌─────────────────┐  │   │
│  │  │  REST API  │  │  WebSocket   │  │  Background      │  │   │
│  │  │  /api/v1/  │  │  /ws         │  │  Tasks (Celery)  │  │   │
│  │  └────────────┘  └──────────────┘  └─────────────────┘  │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌─────────────────────┐   ┌────────────────────────────────┐   │
│  │  Matching Engine    │   │  Analytics Engine              │   │
│  │  sentence-          │   │  scikit-learn  (KMeans,        │   │
│  │  transformers       │   │  AgglomerativeCluster)         │   │
│  │  pgvector ANN       │   │                                │   │
│  └─────────────────────┘   └────────────────────────────────┘   │
└──────────┬──────────────────────────┬───────────────────────────┘
           │                          │
┌──────────▼──────────┐   ┌──────────▼──────────────────────────┐
│    DATA LAYER       │   │          CACHE / BROKER              │
│                     │   │                                      │
│  PostgreSQL 15      │   │  Redis 7                             │
│  + pgvector ext.    │   │  • Session cache                     │
│  (RDS in prod)      │   │  • Pub/Sub for WS events             │
│                     │   │  • Celery task queue                 │
│  Alembic migrations │   │  (ElastiCache in prod)               │
└─────────────────────┘   └──────────────────────────────────────┘
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Backend API** | FastAPI 0.110+, Python 3.11, Uvicorn, SQLAlchemy 2 |
| **Database** | PostgreSQL 15 + pgvector extension |
| **Cache / Broker** | Redis 7 |
| **ML / AI** | sentence-transformers, scikit-learn, NumPy |
| **Frontend** | React 18, Vite, Zustand, Tailwind CSS, React Router v6 |
| **Auth** | JWT (python-jose), bcrypt password hashing |
| **Task Queue** | Celery + Redis |
| **Migrations** | Alembic |
| **Containerisation** | Docker, Docker Compose |
| **Infrastructure** | AWS ECS Fargate, RDS, ElastiCache, S3, CloudFront |
| **IaC** | Terraform |
| **CI/CD** | GitHub Actions |
| **Testing** | pytest, pytest-asyncio, httpx, coverage |
| **Linting** | flake8, black, isort |

---

## Prerequisites

- **Python** 3.11+
- **Node.js** 18+ and **npm** 9+
- **Docker** 24+ and **Docker Compose** v2
- **PostgreSQL** 15 with the `pgvector` extension *(handled automatically in Docker)*
- **Redis** 7 *(handled automatically in Docker)*
- **Make** *(optional but recommended)*

---

## Setup Instructions

### Local Development

```bash
# 1. Clone the repository
git clone https://github.com/SMVEC-CSE/AI-Peer-study-Group-Formation-.git
cd AI-Peer-study-Group-Formation-

# 2. Copy environment template and fill in values
cp .env.example .env

# 3. Install Python dependencies
make install
# or: pip install -r requirements.txt

# 4. Apply database migrations
make migrate
# or: alembic upgrade head

# 5. (Optional) Seed with synthetic data
make seed
# or: python data_pipeline/generators/synthetic_data.py

# 6. Start the API server
make dev
# or: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 7. In a separate terminal, start the React frontend
make frontend-install
make frontend-dev
# or: cd frontend && npm install && npm run dev
```

The API will be available at `http://localhost:8000` and the frontend at `http://localhost:5173`.
Interactive API docs: `http://localhost:8000/docs`

---

### Docker

```bash
# Build and start all services (API, frontend, PostgreSQL, Redis)
make docker-up
# or: docker compose up --build -d

# Check service health
docker compose ps

# View API logs
docker compose logs -f api

# Stop all services
make docker-down
# or: docker compose down
```

Services exposed:

| Service | URL |
|---|---|
| API | `http://localhost:8000` |
| API Docs | `http://localhost:8000/docs` |
| Frontend | `http://localhost:3000` |
| PostgreSQL | `localhost:5432` |
| Redis | `localhost:6379` |

---

### Cloud (AWS)

> **Prerequisites:** AWS CLI configured, Terraform 1.6+, an S3 bucket for Terraform state.

```bash
cd infra/terraform

# Initialise Terraform
terraform init \
  -backend-config="bucket=smvec-tfstate" \
  -backend-config="key=peer-study/terraform.tfstate" \
  -backend-config="region=ap-south-1"

# Review the execution plan
terraform plan -var-file="environments/production.tfvars"

# Apply infrastructure
terraform apply -var-file="environments/production.tfvars"
```

The Terraform configuration provisions:
- **ECS Fargate** cluster with auto-scaling for the API service
- **RDS PostgreSQL 15** (Multi-AZ) with pgvector extension bootstrapped via init script
- **ElastiCache Redis 7** cluster
- **S3 + CloudFront** for the React SPA
- **Application Load Balancer** with HTTPS via ACM
- **ECR** repositories for Docker images
- **Secrets Manager** for database credentials and JWT secret

GitHub Actions workflows (`.github/workflows/`) handle build, test, and ECS deployment on every push to `main`.

---

## API Documentation

Full interactive documentation is auto-generated by FastAPI at `/docs` (Swagger UI) and `/redoc` (ReDoc).

### Key Endpoints

| Method | Path | Description | Auth |
|---|---|---|---|
| `POST` | `/api/v1/auth/register` | Register a new student/faculty | Public |
| `POST` | `/api/v1/auth/login` | Obtain JWT access token | Public |
| `GET` | `/api/v1/students/me` | Get current student profile | JWT |
| `PUT` | `/api/v1/students/me` | Update learning profile | JWT |
| `GET` | `/api/v1/groups/` | List all groups (paginated) | JWT |
| `GET` | `/api/v1/groups/{id}` | Get group details | JWT |
| `POST` | `/api/v1/groups/form` | Trigger AI group formation | Faculty/Admin |
| `PUT` | `/api/v1/groups/{id}/members` | Update group membership | Faculty/Admin |
| `GET` | `/api/v1/analytics/summary` | Faculty analytics overview | Faculty/Admin |
| `GET` | `/api/v1/analytics/export` | Export report as CSV/PDF | Faculty/Admin |
| `WS` | `/ws/{group_id}` | Real-time group chat & events | JWT (query param) |

### Sample Request — Form Groups

```http
POST /api/v1/groups/form
Authorization: Bearer <token>
Content-Type: application/json

{
  "cohort_id": "2024-CSE-A",
  "max_group_size": 5,
  "strategy": "semantic_similarity",
  "schedule_constraint": true
}
```

```json
{
  "job_id": "grp_form_a1b2c3",
  "status": "queued",
  "estimated_completion_seconds": 12
}
```

---

## Screenshots

> _Screenshots and demo GIFs will be added once the UI is finalised._

| View | Preview |
|---|---|
| Student Dashboard | *(coming soon)* |
| Group Formation Wizard | *(coming soon)* |
| Faculty Analytics Panel | *(coming soon)* |
| Real-Time Group Chat | *(coming soon)* |

---

## Contributing

Contributions are welcome! Please follow the steps below.

1. **Fork** the repository and create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. **Code style** — run linters before committing:
   ```bash
   make lint
   ```
3. **Tests** — all new code must have corresponding tests:
   ```bash
   make test
   ```
4. **Commit messages** follow [Conventional Commits](https://www.conventionalcommits.org/):
   - `feat:` new feature
   - `fix:` bug fix
   - `docs:` documentation only
   - `test:` adding/updating tests
   - `chore:` build system or tooling changes
5. **Pull Request** — open a PR against the `main` branch with a clear description of *what* and *why*.
6. At least one approval from a **SMVEC maintainer** is required before merging.

### Code of Conduct

This project adheres to the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/). By participating you agree to uphold this standard.

---

## License

```
MIT License

Copyright (c) 2024 Sri Manakula Vinayagar Engineering College, Puducherry

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

<p align="center">
  Built with ❤️ at <strong>SMVEC, Puducherry</strong>
</p>