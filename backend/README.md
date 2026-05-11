# Job Portal — FastAPI + MongoDB Backend

A production-ready REST API for a job portal with separate flows for **job seekers (users)** and **employers (hosts)**.

---

## Project Structure

```
job_portal/
├── main.py                  # App entry point, CORS, router registration
├── requirements.txt
├── .env.example             # Copy to .env and configure
├── core/
│   ├── database.py          # Motor (async MongoDB) client + index setup
│   └── security.py          # JWT creation/validation, password hashing, role guards
├── models/
│   └── schemas.py           # All Pydantic request/response models + enums
└── routers/
    ├── auth.py              # POST /api/auth/signup, /login, GET /me
    ├── jobs.py              # GET  /api/jobs/search, /api/jobs/{id}   (user role)
    └── host.py              # CRUD /api/host/jobs/*                   (host role)
```

---

## Setup & Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env — set MONGO_URL and SECRET_KEY

# 3. Run the development server
uvicorn main:app --reload --port 8000
```

Open **http://localhost:8000/docs** for the interactive Swagger UI.

---

## API Reference

### Auth endpoints (public)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/signup` | Register as `user` or `host` |
| POST | `/api/auth/login`  | Login — returns JWT token |
| GET  | `/api/auth/me`     | Get own profile (requires token) |

**Signup body:**
```json
{
  "name": "Rahul Sharma",
  "email": "rahul@example.com",
  "password": "secret123",
  "role": "user"        // or "host"
}
```

**Login body:**
```json
{ "email": "rahul@example.com", "password": "secret123" }
```

**Token response:**
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "role": "user",
  "name": "Rahul Sharma",
  "user_id": "664abc..."
}
```

---

### User — job search (role: `user`)

All requests require `Authorization: Bearer <token>`.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/jobs/search` | Search & filter jobs |
| GET | `/api/jobs/{id}`   | Get full job details |

**Search query params:**

| Param | Type | Example |
|-------|------|---------|
| `q` | string | `react developer` |
| `location` | string | `Delhi` |
| `job_type` | enum | `full-time`, `part-time`, `remote`, `contract`, `internship` |
| `experience_level` | enum | `entry`, `mid`, `senior`, `lead` |
| `category` | string | `Engineering` |
| `salary_min` | int | `50000` |
| `salary_max` | int | `150000` |
| `page` | int | `1` |
| `page_size` | int | `10` |

---

### Host — job management (role: `host`)

All requests require `Authorization: Bearer <token>` with `role: host`.

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST   | `/api/host/jobs`               | Create a new job listing |
| GET    | `/api/host/jobs`               | List all your job listings |
| GET    | `/api/host/jobs/{id}`          | Get one listing |
| PATCH  | `/api/host/jobs/{id}`          | Update any fields |
| DELETE | `/api/host/jobs/{id}`          | Soft-delete (deactivate) |
| DELETE | `/api/host/jobs/{id}/permanent`| Hard-delete from DB |
| GET    | `/api/host/stats`              | Dashboard stats |

**Create job body:**
```json
{
  "title": "Senior React Developer",
  "description": "We are looking for a skilled React developer...",
  "company": "Acme Corp",
  "location": "Bangalore",
  "job_type": "full-time",
  "experience_level": "senior",
  "category": "Engineering",
  "skills": ["React", "TypeScript", "Node.js"],
  "salary": { "min": 1200000, "max": 1800000, "currency": "INR" },
  "is_active": true
}
```

---

## MongoDB Collections

### `users`
```js
{
  _id, name, email, password (bcrypt), role ("user"|"host"), created_at
}
```

### `jobs`
```js
{
  _id, title, description, company, location,
  job_type, experience_level, category,
  skills: [...],
  salary: { min, max, currency },
  is_active, host_id (ref users._id),
  posted_at, updated_at
}
```

**Indexes:**
- `users.email` — unique
- `jobs` — text index on `title + description + skills`
- `jobs.location`, `job_type`, `category`, `is_active`, `host_id`, `posted_at`

---

## Security

- Passwords hashed with **bcrypt** via `passlib`
- Auth via **JWT** (HS256), 24-hour expiry
- Role-based access control: `user` routes and `host` routes are guarded separately
- Hosts can only read/update/delete **their own** job listings
