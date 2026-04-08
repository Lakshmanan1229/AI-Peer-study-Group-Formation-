# API Documentation

## Base URL

All API endpoints are versioned and accessible under:

```
http://localhost:8000/api/v1
```

Production:

```
https://api.smvec-peerstudy.example.com/api/v1
```

## Authentication

The API uses JWT Bearer token authentication. Include the access token in the `Authorization` header:

```
Authorization: Bearer <access_token>
```

- **Access tokens** expire after 30 minutes
- **Refresh tokens** expire after 7 days
- Tokens are issued upon registration or login

---

## System Endpoints

### Health Check

```
GET /health
```

Returns the health status of the API server. No authentication required.

**Response** `200 OK`:
```json
{
  "status": "healthy",
  "environment": "production",
  "version": "1.0.0"
}
```

### Root

```
GET /
```

Returns basic service information.

**Response** `200 OK`:
```json
{
  "service": "AI Peer Study Group Formation API",
  "version": "1.0.0",
  "docs": "/docs"
}
```

---

## Auth Endpoints

### Register

```
POST /api/v1/auth/register
```

Create a new student account. No authentication required.

**Request Body:**
```json
{
  "email": "student@smvec.ac.in",
  "password": "securePassword123",
  "full_name": "Arun Kumar",
  "department": "CSE",
  "year": 3,
  "cgpa": 8.5,
  "learning_pace": "moderate"
}
```

| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| email | string | Yes | Valid email, unique |
| password | string | Yes | Minimum 8 characters |
| full_name | string | Yes | Max 255 characters |
| department | string | Yes | One of: `CSE`, `IT`, `ECE` |
| year | integer | Yes | 1–4 |
| cgpa | float | Yes | 0.0–10.0 |
| learning_pace | string | Yes | One of: `slow`, `moderate`, `fast` |

**Response** `201 Created`:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Error Responses:**

| Status | Description |
|--------|-------------|
| `400 Bad Request` | Validation error (invalid email, weak password, etc.) |
| `409 Conflict` | Email already registered |

```json
{
  "detail": "Email already registered"
}
```

---

### Login

```
POST /api/v1/auth/login
```

Authenticate and receive a JWT token pair. No authentication required.

**Request Body:**
```json
{
  "email": "student@smvec.ac.in",
  "password": "securePassword123"
}
```

| Field | Type | Required |
|-------|------|----------|
| email | string | Yes |
| password | string | Yes |

**Response** `200 OK`:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Error Responses:**

| Status | Description |
|--------|-------------|
| `401 Unauthorized` | Invalid email or password |

```json
{
  "detail": "Invalid credentials"
}
```

---

### Refresh Token

```
POST /api/v1/auth/refresh
```

Exchange a valid refresh token for a new token pair. No authentication required.

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response** `200 OK`:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Error Responses:**

| Status | Description |
|--------|-------------|
| `401 Unauthorized` | Invalid or expired refresh token |

---

## Student Endpoints

All student endpoints require JWT authentication.

### Get My Profile

```
GET /api/v1/students/me
```

Retrieve the authenticated student's profile.

**Response** `200 OK`:
```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "email": "student@smvec.ac.in",
  "full_name": "Arun Kumar",
  "department": "CSE",
  "year": 3,
  "cgpa": 8.5,
  "learning_pace": "moderate",
  "role": "student",
  "is_active": true,
  "goals": "Master data structures and algorithms, learn system design",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-20T14:00:00Z"
}
```

**Error Responses:**

| Status | Description |
|--------|-------------|
| `401 Unauthorized` | Missing or invalid token |
| `404 Not Found` | Student profile not found |

---

### Update My Profile

```
PUT /api/v1/students/me
```

Update the authenticated student's profile fields.

**Request Body** (all fields optional):
```json
{
  "full_name": "Arun Kumar S",
  "department": "CSE",
  "year": 4,
  "cgpa": 8.7,
  "learning_pace": "fast"
}
```

**Response** `200 OK`:
```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "email": "student@smvec.ac.in",
  "full_name": "Arun Kumar S",
  "department": "CSE",
  "year": 4,
  "cgpa": 8.7,
  "learning_pace": "fast",
  "role": "student",
  "is_active": true,
  "goals": "Master data structures and algorithms, learn system design",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-02-01T09:15:00Z"
}
```

---

### Get My Skills

```
GET /api/v1/students/me/skills
```

Retrieve all skill assessments for the authenticated student.

**Response** `200 OK`:
```json
{
  "skills": [
    {
      "id": 1,
      "subject": "Data Structures",
      "self_rating": 8,
      "peer_rating": 7.5,
      "grade_points": 9.0,
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-20T14:00:00Z"
    },
    {
      "id": 2,
      "subject": "Machine Learning",
      "self_rating": 6,
      "peer_rating": null,
      "grade_points": 7.5,
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

---

### Update My Skills

```
PUT /api/v1/students/me/skills
```

Bulk upsert skill assessments. Existing skills are updated; new skills are created.

**Request Body:**
```json
{
  "skills": [
    {
      "subject": "Data Structures",
      "self_rating": 8,
      "grade_points": 9.0
    },
    {
      "subject": "Machine Learning",
      "self_rating": 7,
      "grade_points": 8.0
    },
    {
      "subject": "Database Systems",
      "self_rating": 9,
      "grade_points": 9.5
    }
  ]
}
```

| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| subject | string | Yes | Max 255 characters |
| self_rating | integer | Yes | 1–10 |
| grade_points | float | No | 0.0–10.0 |

**Response** `200 OK`:
```json
{
  "skills": [
    {
      "id": 1,
      "subject": "Data Structures",
      "self_rating": 8,
      "peer_rating": 7.5,
      "grade_points": 9.0,
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-02-01T09:00:00Z"
    },
    {
      "id": 2,
      "subject": "Machine Learning",
      "self_rating": 7,
      "peer_rating": null,
      "grade_points": 8.0,
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-02-01T09:00:00Z"
    },
    {
      "id": 3,
      "subject": "Database Systems",
      "self_rating": 9,
      "peer_rating": null,
      "grade_points": 9.5,
      "created_at": "2024-02-01T09:00:00Z",
      "updated_at": "2024-02-01T09:00:00Z"
    }
  ]
}
```

---

### Update My Schedule

```
PUT /api/v1/students/me/schedule
```

Bulk update weekly availability slots.

**Request Body:**
```json
{
  "slots": [
    { "day_of_week": 0, "slot": "morning", "is_available": true },
    { "day_of_week": 0, "slot": "afternoon", "is_available": false },
    { "day_of_week": 0, "slot": "evening", "is_available": true },
    { "day_of_week": 1, "slot": "morning", "is_available": true },
    { "day_of_week": 1, "slot": "afternoon", "is_available": true },
    { "day_of_week": 1, "slot": "evening", "is_available": false }
  ]
}
```

| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| day_of_week | integer | Yes | 0 (Monday) – 6 (Sunday) |
| slot | string | Yes | One of: `morning`, `afternoon`, `evening` |
| is_available | boolean | Yes | — |

**Response** `200 OK`:
```json
{
  "slots": [
    { "id": 1, "day_of_week": 0, "slot": "morning", "is_available": true },
    { "id": 2, "day_of_week": 0, "slot": "afternoon", "is_available": false },
    { "id": 3, "day_of_week": 0, "slot": "evening", "is_available": true },
    { "id": 4, "day_of_week": 1, "slot": "morning", "is_available": true },
    { "id": 5, "day_of_week": 1, "slot": "afternoon", "is_available": true },
    { "id": 6, "day_of_week": 1, "slot": "evening", "is_available": false }
  ]
}
```

---

### Update My Goals

```
PUT /api/v1/students/me/goals
```

Update study goals. The backend automatically generates a 384-dimensional embedding using `all-MiniLM-L6-v2` and stores it in pgvector for semantic matching.

**Request Body:**
```json
{
  "goals": "Master data structures and algorithms, prepare for competitive programming, learn system design patterns"
}
```

**Response** `200 OK`:
```json
{
  "goals": "Master data structures and algorithms, prepare for competitive programming, learn system design patterns",
  "updated_at": "2024-02-01T09:15:00Z"
}
```

---

## Group Endpoints

All group endpoints require JWT authentication.

### Get My Group

```
GET /api/v1/groups/my-group
```

Retrieve the authenticated student's current active study group with full details.

**Response** `200 OK`:
```json
{
  "id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "name": "CSE Group Alpha",
  "department": "CSE",
  "status": "active",
  "max_size": 6,
  "complementary_score": 0.82,
  "schedule_overlap_count": 5,
  "goal_similarity_score": 0.76,
  "members": [
    {
      "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "full_name": "Arun Kumar",
      "department": "CSE",
      "year": 3,
      "cgpa": 8.5,
      "learning_pace": "moderate",
      "role": "leader",
      "strengths": ["Data Structures", "Database Systems"],
      "weaknesses": ["Machine Learning"]
    },
    {
      "id": "c3d4e5f6-a7b8-9012-cdef-123456789012",
      "full_name": "Priya Sharma",
      "department": "CSE",
      "year": 3,
      "cgpa": 9.0,
      "learning_pace": "fast",
      "role": "member",
      "strengths": ["Machine Learning", "Mathematics"],
      "weaknesses": ["Web Development"]
    }
  ],
  "suggested_meeting_times": [
    { "day_of_week": 1, "slot": "afternoon" },
    { "day_of_week": 3, "slot": "evening" }
  ],
  "created_at": "2024-01-20T08:00:00Z"
}
```

**Error Responses:**

| Status | Description |
|--------|-------------|
| `404 Not Found` | Student is not in any active group |

```json
{
  "detail": "No active group found"
}
```

---

### Get Group Health

```
GET /api/v1/groups/my-group/health
```

Retrieve the health score and contributing factors for the student's current group.

**Response** `200 OK`:
```json
{
  "group_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "health_score": 78,
  "factors": {
    "skill_complementarity": 0.82,
    "schedule_overlap": 0.70,
    "goal_alignment": 0.76,
    "peer_feedback_avg": 4.2,
    "session_attendance_rate": 0.85,
    "activity_level": 0.90
  },
  "recommendations": [
    "Schedule a group session during your common free slots on Tuesday afternoon",
    "Priya can mentor the group on Machine Learning concepts",
    "Consider adding more practice problems for Database Systems"
  ]
}
```

---

### Create Group Session

```
POST /api/v1/groups/my-group/sessions
```

Schedule a new study session for the student's current group.

**Request Body:**
```json
{
  "scheduled_at": "2024-02-05T14:00:00Z",
  "duration_minutes": 90,
  "location": "Library Room 204",
  "session_type": "offline",
  "notes": "Focus on binary trees and graph traversal algorithms"
}
```

| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| scheduled_at | datetime | Yes | ISO 8601 format, must be in the future |
| duration_minutes | integer | Yes | 15–480 |
| location | string | No | Max 500 characters |
| session_type | string | Yes | One of: `online`, `offline` |
| notes | string | No | Free text |

**Response** `201 Created`:
```json
{
  "id": "d4e5f6a7-b8c9-0123-defa-234567890123",
  "group_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "scheduled_at": "2024-02-05T14:00:00Z",
  "duration_minutes": 90,
  "location": "Library Room 204",
  "session_type": "offline",
  "notes": "Focus on binary trees and graph traversal algorithms",
  "attendance": null,
  "created_by": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "created_at": "2024-02-01T10:00:00Z"
}
```

---

### Get Group Resources

```
GET /api/v1/groups/my-group/resources
```

Retrieve recommended learning resources tailored to the group's collective skill gaps.

**Response** `200 OK`:
```json
{
  "group_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "resources": [
    {
      "title": "Introduction to Algorithms (CLRS)",
      "type": "book",
      "subject": "Data Structures",
      "difficulty": "intermediate",
      "url": "https://example.com/clrs",
      "relevance_score": 0.92
    },
    {
      "title": "Machine Learning Crash Course",
      "type": "video",
      "subject": "Machine Learning",
      "difficulty": "beginner",
      "url": "https://example.com/ml-course",
      "relevance_score": 0.88
    }
  ]
}
```

---

## Feedback Endpoints

All feedback endpoints require JWT authentication.

### Submit Feedback

```
POST /api/v1/feedback/submit
```

Submit peer feedback for one or more group members after a study session.

**Request Body:**
```json
{
  "feedbacks": [
    {
      "reviewee_id": "c3d4e5f6-a7b8-9012-cdef-123456789012",
      "rating": 5,
      "helpfulness_score": 4,
      "comment": "Excellent explanation of neural networks. Very patient and clear.",
      "is_anonymous": false
    },
    {
      "reviewee_id": "e5f6a7b8-c9d0-1234-efab-345678901234",
      "rating": 4,
      "helpfulness_score": 3,
      "comment": "Good contribution to the discussion.",
      "is_anonymous": true
    }
  ]
}
```

| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| reviewee_id | UUID | Yes | Must be a member of the same group |
| rating | integer | Yes | 1–5 |
| helpfulness_score | integer | Yes | 1–5 |
| comment | string | No | Free text |
| is_anonymous | boolean | No | Default: `false` |

**Response** `201 Created`:
```json
{
  "submitted": 2,
  "feedbacks": [
    {
      "id": "f6a7b8c9-d0e1-2345-fabc-456789012345",
      "reviewer_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "reviewee_id": "c3d4e5f6-a7b8-9012-cdef-123456789012",
      "group_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
      "rating": 5,
      "helpfulness_score": 4,
      "comment": "Excellent explanation of neural networks. Very patient and clear.",
      "is_anonymous": false,
      "created_at": "2024-02-01T16:00:00Z"
    },
    {
      "id": "a7b8c9d0-e1f2-3456-abcd-567890123456",
      "reviewer_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "reviewee_id": "e5f6a7b8-c9d0-1234-efab-345678901234",
      "group_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
      "rating": 4,
      "helpfulness_score": 3,
      "comment": "Good contribution to the discussion.",
      "is_anonymous": true,
      "created_at": "2024-02-01T16:00:00Z"
    }
  ]
}
```

**Error Responses:**

| Status | Description |
|--------|-------------|
| `400 Bad Request` | Cannot review yourself, or reviewee not in same group |
| `404 Not Found` | Reviewee not found |

---

### Get Group Feedback Report

```
GET /api/v1/feedback/group-report
```

Retrieve an aggregated feedback report for the student's current group.

**Response** `200 OK`:
```json
{
  "group_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "total_feedbacks": 12,
  "average_rating": 4.3,
  "average_helpfulness": 3.8,
  "member_summaries": [
    {
      "student_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "full_name": "Arun Kumar",
      "avg_rating": 4.5,
      "avg_helpfulness": 4.0,
      "feedback_count": 4
    },
    {
      "student_id": "c3d4e5f6-a7b8-9012-cdef-123456789012",
      "full_name": "Priya Sharma",
      "avg_rating": 4.8,
      "avg_helpfulness": 4.5,
      "feedback_count": 4
    }
  ]
}
```

---

## Recommendation Endpoints

All recommendation endpoints require JWT authentication.

### Get Resource Recommendations

```
GET /api/v1/recommendations/resources
```

Get personalized learning resource recommendations based on the student's skill gaps, goals, and learning pace.

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| subject | string | No | Filter by specific subject |
| limit | integer | No | Max results (default: 10, max: 50) |

**Response** `200 OK`:
```json
{
  "recommendations": [
    {
      "title": "Hands-On Machine Learning with Scikit-Learn",
      "type": "book",
      "subject": "Machine Learning",
      "difficulty": "intermediate",
      "url": "https://example.com/hands-on-ml",
      "reason": "Based on your self-rating of 6/10 in Machine Learning",
      "relevance_score": 0.95
    },
    {
      "title": "System Design Primer",
      "type": "article",
      "subject": "System Design",
      "difficulty": "intermediate",
      "url": "https://example.com/system-design",
      "reason": "Aligned with your goal: learn system design patterns",
      "relevance_score": 0.89
    },
    {
      "title": "LeetCode Top 100 Problems",
      "type": "course",
      "subject": "Data Structures",
      "difficulty": "advanced",
      "url": "https://example.com/leetcode-top100",
      "reason": "Strengthen your already strong DSA skills for competitive programming",
      "relevance_score": 0.85
    }
  ]
}
```

---

### Get Mentor Recommendations

```
GET /api/v1/recommendations/mentors
```

Find peer mentors with complementary skills who can help in areas where the student needs improvement.

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| subject | string | No | Filter by specific subject |
| limit | integer | No | Max results (default: 5, max: 20) |

**Response** `200 OK`:
```json
{
  "mentors": [
    {
      "student_id": "c3d4e5f6-a7b8-9012-cdef-123456789012",
      "full_name": "Priya Sharma",
      "department": "CSE",
      "year": 3,
      "subject": "Machine Learning",
      "their_rating": 9,
      "your_rating": 6,
      "compatibility_score": 0.88,
      "common_free_slots": [
        { "day_of_week": 1, "slot": "afternoon" },
        { "day_of_week": 3, "slot": "evening" }
      ]
    },
    {
      "student_id": "e5f6a7b8-c9d0-1234-efab-345678901234",
      "full_name": "Rahul Dev",
      "department": "CSE",
      "year": 4,
      "subject": "System Design",
      "their_rating": 8,
      "your_rating": 4,
      "compatibility_score": 0.82,
      "common_free_slots": [
        { "day_of_week": 2, "slot": "morning" }
      ]
    }
  ]
}
```

---

## Admin Endpoints

All admin endpoints require JWT authentication with `admin` role.

### Trigger Group Formation

```
POST /api/v1/admin/trigger-grouping
```

Run the full AI group formation pipeline. This operation processes all ungrouped students through the ML pipeline (feature engineering → clustering → optimization) and creates new study groups.

**Request Body** (optional):
```json
{
  "department": "CSE",
  "max_group_size": 6,
  "min_group_size": 3
}
```

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| department | string | No | All | Filter students by department |
| max_group_size | integer | No | 6 | Maximum members per group |
| min_group_size | integer | No | 3 | Minimum members per group |

**Response** `200 OK`:
```json
{
  "status": "completed",
  "groups_created": 8,
  "students_grouped": 45,
  "students_unmatched": 2,
  "average_complementary_score": 0.78,
  "average_schedule_overlap": 4.2,
  "average_goal_similarity": 0.72,
  "execution_time_seconds": 12.5
}
```

**Error Responses:**

| Status | Description |
|--------|-------------|
| `403 Forbidden` | User does not have admin role |
| `409 Conflict` | Group formation already in progress |

---

### Get Analytics Dashboard

```
GET /api/v1/admin/analytics/dashboard
```

Retrieve system-wide statistics and analytics.

**Response** `200 OK`:
```json
{
  "total_students": 150,
  "active_students": 142,
  "total_groups": 25,
  "active_groups": 23,
  "total_sessions": 87,
  "total_feedbacks": 324,
  "department_breakdown": {
    "CSE": { "students": 65, "groups": 11 },
    "IT": { "students": 48, "groups": 8 },
    "ECE": { "students": 37, "groups": 6 }
  },
  "average_group_health": 74.5,
  "average_session_attendance": 0.82,
  "average_feedback_rating": 4.1,
  "groups_by_status": {
    "active": 23,
    "inactive": 1,
    "disbanded": 1
  }
}
```

---

### List All Students

```
GET /api/v1/admin/students
```

Retrieve a paginated list of all registered students.

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| page | integer | No | 1 | Page number |
| per_page | integer | No | 20 | Results per page (max 100) |
| department | string | No | All | Filter by department |
| year | integer | No | All | Filter by year |
| search | string | No | — | Search by name or email |

**Response** `200 OK`:
```json
{
  "students": [
    {
      "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "email": "student@smvec.ac.in",
      "full_name": "Arun Kumar",
      "department": "CSE",
      "year": 3,
      "cgpa": 8.5,
      "learning_pace": "moderate",
      "is_active": true,
      "group_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 150,
  "page": 1,
  "per_page": 20,
  "pages": 8
}
```

---

### List All Groups

```
GET /api/v1/admin/groups
```

Retrieve a paginated list of all study groups with summary statistics.

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| page | integer | No | 1 | Page number |
| per_page | integer | No | 20 | Results per page (max 100) |
| department | string | No | All | Filter by department |
| status | string | No | All | Filter by status (`active`, `inactive`, `disbanded`) |

**Response** `200 OK`:
```json
{
  "groups": [
    {
      "id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
      "name": "CSE Group Alpha",
      "department": "CSE",
      "status": "active",
      "member_count": 5,
      "max_size": 6,
      "complementary_score": 0.82,
      "schedule_overlap_count": 5,
      "goal_similarity_score": 0.76,
      "session_count": 4,
      "average_feedback_rating": 4.3,
      "created_at": "2024-01-20T08:00:00Z"
    }
  ],
  "total": 25,
  "page": 1,
  "per_page": 20,
  "pages": 2
}
```

---

## Error Response Format

All error responses follow a consistent format:

```json
{
  "detail": "Human-readable error message"
}
```

For validation errors (422):

```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

### Common Error Codes

| Status Code | Description |
|-------------|-------------|
| `400 Bad Request` | Invalid request body or parameters |
| `401 Unauthorized` | Missing, invalid, or expired authentication token |
| `403 Forbidden` | Insufficient permissions (e.g., non-admin accessing admin endpoints) |
| `404 Not Found` | Requested resource does not exist |
| `409 Conflict` | Resource already exists or operation conflicts with current state |
| `422 Unprocessable Entity` | Request body validation failed (Pydantic error) |
| `429 Too Many Requests` | Rate limit exceeded |
| `500 Internal Server Error` | Unexpected server error |

---

## Rate Limiting

API endpoints are rate-limited using Redis-backed counters:

| Endpoint Category | Limit |
|-------------------|-------|
| Auth (login/register) | 10 requests per minute per IP |
| Student endpoints | 60 requests per minute per user |
| Admin endpoints | 30 requests per minute per user |
| Group formation trigger | 1 request per 5 minutes |

When rate limited, the API returns:

```
HTTP/1.1 429 Too Many Requests
Retry-After: 30
```

```json
{
  "detail": "Rate limit exceeded. Try again in 30 seconds."
}
```

---

## Interactive API Documentation

The API provides built-in interactive documentation:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI Schema**: `http://localhost:8000/openapi.json`

These endpoints are automatically generated from the FastAPI route definitions and Pydantic schemas, and always reflect the current state of the API.
