# TaskFlow — Scalable REST API with JWT Auth & RBAC

A production-ready REST API built with **FastAPI**, **SQLite/SQLAlchemy**, **JWT authentication**, and a clean **Vanilla JS frontend**. Deployable on Railway.app in one click.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI (Python 3.11+) |
| Database | SQLite + SQLAlchemy ORM |
| Auth | JWT (python-jose) + bcrypt (passlib) |
| Frontend | Vanilla HTML/CSS/JS (single file) |
| Deployment | Railway.app (Procfile included) |

---

## Quick Start

### 1. Clone & Install

```bash
git clone <your-repo-url>
cd taskflow
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run

```bash
uvicorn main:app --reload
```

- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- Frontend: http://localhost:8000  *(served automatically)*

---

## Creating an Admin User

The register endpoint creates `user` role by default. To promote a user to admin, run this one-time script:

```bash
python - <<'EOF'
from database import SessionLocal
from models import User
db = SessionLocal()
user = db.query(User).filter(User.username == "your_username").first()
if user:
    user.role = "admin"
    db.commit()
    print(f"Promoted {user.username} to admin")
else:
    print("User not found")
db.close()
EOF
```

---

## API Endpoints

### Auth & Users

| Method | Endpoint | Auth | Role | Description |
|---|---|---|---|---|
| POST | `/api/v1/auth/register` | None | — | Register new user |
| POST | `/api/v1/auth/login` | None | — | Login, returns JWT |
| GET | `/api/v1/users/me` | JWT | any | Get own profile |
| GET | `/api/v1/users/` | JWT | admin | List all users |

### Tasks

| Method | Endpoint | Auth | Role | Description |
|---|---|---|---|---|
| POST | `/api/v1/tasks/` | JWT | any | Create a task |
| GET | `/api/v1/tasks/` | JWT | any/admin | List tasks (own / all) |
| GET | `/api/v1/tasks/{id}` | JWT | owner/admin | Get task by ID |
| PUT | `/api/v1/tasks/{id}` | JWT | owner/admin | Update task |
| DELETE | `/api/v1/tasks/{id}` | JWT | owner/admin | Delete task |

### Status Codes

| Code | Meaning |
|---|---|
| 200 | OK |
| 201 | Created |
| 204 | No Content (delete) |
| 400 | Bad Request (validation) |
| 401 | Unauthorized (missing/expired token) |
| 403 | Forbidden (insufficient role) |
| 404 | Not Found |

---

## JWT Authentication

All protected routes require the `Authorization` header:

```
Authorization: Bearer <your_access_token>
```

Tokens expire after **30 minutes**. Re-login to get a new token.

---

## Deployment on Railway.app

1. Push the repo to GitHub
2. Create a new project on [Railway.app](https://railway.app)
3. Connect the GitHub repo
4. Railway auto-detects the `Procfile` and deploys

The `Procfile` runs:
```
uvicorn main:app --host 0.0.0.0 --port $PORT
```

---

## Scalability Notes

This project is architected to scale. Here's the roadmap beyond SQLite:

### Database
- **PostgreSQL** via `asyncpg` + `databases` for async queries at scale
- Replace `SQLALCHEMY_DATABASE_URL` with a Postgres connection string — no other code changes needed (SQLAlchemy abstracts the driver)
- Add **Alembic** for schema migrations: `alembic init alembic && alembic revision --autogenerate`

### Caching
- Add **Redis** with `fastapi-cache2` for caching task lists and user lookups
- Reduces DB hits on read-heavy endpoints like `GET /tasks/` by 90%+

### Auth at Scale
- Rotate the `SECRET_KEY` via environment variable (`os.environ.get("SECRET_KEY")`)
- Add **refresh tokens** (long-lived) + short-lived access tokens to avoid frequent re-logins
- Add **rate limiting** with `slowapi` to prevent brute-force attacks on `/auth/login`

### Microservices Path
```
taskflow/
  auth-service/     → handles register/login, issues JWTs
  task-service/     → CRUD for tasks, validates JWT internally
  user-service/     → user management, admin ops
  api-gateway/      → nginx / Traefik routes requests to services
```

Each service is a separate FastAPI app in its own container, communicating via HTTP or message queues (RabbitMQ / Redis Streams).

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
services:
  api:
    build: .
    ports: ["8000:8000"]
    environment:
      - SECRET_KEY=your-secure-secret
```

---

## Project Structure

```
taskflow/
├── main.py              # FastAPI app + CORS + startup
├── database.py          # SQLAlchemy engine + session
├── models.py            # ORM models (User, Task)
├── schemas.py           # Pydantic v2 schemas
├── auth.py              # JWT + bcrypt utilities
├── routers/
│   ├── users.py         # Auth + user endpoints
│   └── tasks.py         # Task CRUD endpoints
├── frontend/
│   └── index.html       # Complete SPA (no build step)
├── requirements.txt
├── Procfile
└── README.md
```

---

## License

MIT
