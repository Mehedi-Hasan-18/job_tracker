# JobTrackr — Backend

A Django REST Framework backend for JobTrackr, a full-stack job application tracker. Features JWT authentication, PostgreSQL, async email reminders via Celery, and auto-ghost logic for stale applications.

## Live Demo

🔗 [https://job-tracker-75n4.onrender.com](https://job-tracker-75n4.onrender.com)

> Frontend: [https://jobtraker.netlify.app/](https://jobtraker.netlify.app/)

---

## Features

- JWT authentication with token blacklisting on logout
- Full CRUD for job applications per authenticated user
- Auto-ghost applications with no activity after 30 days
- Async email reminders via Celery + Upstash Redis
- Daily scheduled task via Celery Beat
- Stats endpoint returning application counts by status
- Search and ordering on applications via DRF filters
- Django Admin panel with inline reminders and filters
- PostgreSQL database hosted on Neon

---

## Tech Stack

| Tool | Purpose |
|---|---|
| Django 5 | Web framework |
| Django REST Framework | REST API |
| SimpleJWT | JWT authentication |
| PostgreSQL (Neon) | Database |
| Celery | Async task queue |
| Redis (Upstash) | Celery broker + result backend |
| Gunicorn | Production WSGI server |
| Whitenoise | Static file serving |
| django-cors-headers | CORS for React frontend |
| python-decouple | Environment variable management |

---

## Project Structure

```
jobtrackr/
│   ├── __init__.py          # Celery app import
│   ├── celery.py            # Celery configuration
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── accounts/
│   ├── models.py            # CustomUser model
│   ├── views.py             # Register, login, logout
│   └── urls.py
├── tracker/
│   ├── models.py            # Application, Reminder
│   ├── serializers.py       # DRF serializers
│   ├── views.py             # ViewSets + stats endpoint
│   ├── tasks.py             # Celery tasks
│   └── urls.py              # Router registration
├── requirements.txt
├── .env.example
└── manage.py
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL database (local or [Neon](https://neon.tech))
- Redis instance (local or [Upstash](https://upstash.com))

### Installation

```bash
# Clone the repo
git clone https://github.com/Mehedi-Hasan-18/job_tracker
cd job_tracker

# Create and activate virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
```

Edit `.env` with your values:
```env
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=jobtrackr_db
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=your_neon_host
DB_PORT=5432

CELERY_BROKER_URL=rediss://default:password@your-upstash-endpoint:6379
CELERY_RESULT_BACKEND=rediss://default:password@your-upstash-endpoint:6379

EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your@gmail.com
EMAIL_HOST_PASSWORD=your_16_char_app_password

CORS_ALLOWED_ORIGINS=http://localhost:5173
```

```bash
# Run migrations
python manage.py migrate

# Create superuser for admin panel
python manage.py createsuperuser

# Start the development server
python manage.py runserver
```

---

## Running Celery

You need 3 terminals running simultaneously during development:

```bash
# Terminal 1 — Django
python manage.py runserver

# Terminal 2 — Celery worker
celery -A job_tracker worker --loglevel=info

# Terminal 3 — Celery beat scheduler
celery -A job_tracker beat --loglevel=info
```

---

## Environment Variables

| Variable | Description |
|---|---|
| `SECRET_KEY` | Django secret key |
| `DEBUG` | `True` for dev, `False` for production |
| `ALLOWED_HOSTS` | Comma-separated allowed hosts |
| `DB_NAME` | PostgreSQL database name |
| `DB_USER` | PostgreSQL username |
| `DB_PASSWORD` | PostgreSQL password |
| `DB_HOST` | PostgreSQL host (Neon endpoint) |
| `DB_PORT` | PostgreSQL port (default 5432) |
| `CELERY_BROKER_URL` | Redis URL for Celery broker |
| `CELERY_RESULT_BACKEND` | Redis URL for Celery results |
| `EMAIL_HOST_USER` | Gmail address |
| `EMAIL_HOST_PASSWORD` | Gmail App Password (not your login password) |
| `CORS_ALLOWED_ORIGINS` | Comma-separated allowed frontend origins |

---

## API Endpoints

### Auth

| Method | Endpoint | Description | Auth required |
|---|---|---|---|
| POST | `/api/auth/register/` | Register new user, returns JWT | No |
| POST | `/api/auth/login/` | Login, returns JWT | No |
| POST | `/api/auth/logout/` | Blacklist refresh token | Yes |

### Applications

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/applications/` | List all applications for current user |
| POST | `/api/applications/` | Create a new application |
| GET | `/api/applications/:id/` | Retrieve single application |
| PATCH | `/api/applications/:id/` | Update application |
| DELETE | `/api/applications/:id/` | Delete application |
| GET | `/api/applications/stats/` | Get status counts |

### Reminders

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/reminders/` | List all reminders for current user |
| POST | `/api/reminders/` | Create reminder (schedules email automatically) |
| DELETE | `/api/reminders/:id/` | Delete reminder |

All application and reminder endpoints require `Authorization: Bearer <access_token>` header.

---

## Request & Response Examples

### Register
```json
POST /api/auth/register/
{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "securepassword"
}

Response 200:
{
    "access": "eyJ...",
    "refresh": "eyJ...",
    "user": "johndoe"
}
```

### Create Application
```json
POST /api/applications/
{
    "company": "Google",
    "role": "Backend Engineer",
    "status": "applied",
    "applied_date": "2026-04-01",
    "notes": "Applied via referral"
}
```

### Stats Response
```json
GET /api/applications/stats/
{
    "total": 12,
    "applied": 5,
    "interview": 3,
    "offer": 1,
    "rejected": 2,
    "ghost": 1
}
```

---

## Admin Panel

Visit `http://localhost:8000/admin` after creating a superuser.

Features available in the admin:
- View and manage all users
- View all applications with filters by status and date
- Add/edit reminders inline within an application
- Search applications by company, role, or username

---

## Celery Tasks

### `send_reminder_email`
Triggered when a reminder is created via the API. Sends an email to the user at the scheduled `remind_at` time using `apply_async` with a countdown.

### `auto_ghost_applications`
Runs daily at 9am via Celery Beat. Finds all applications with status `applied` and no activity in the last 30 days, and updates their status to `ghost`.

---

## Deployment (Render)

**Build Command:**
```
pip install -r requirements.txt && python manage.py collectstatic --no-input && python manage.py migrate
```

**Start Command:**
```
gunicorn job_tracker.wsgi:application --bind 0.0.0.0:$PORT
```

**Celery Worker** (separate Background Worker service on Render):
```
celery -A job_tracker worker --loglevel=info
```

Set all `.env` variables in the Render dashboard under **Environment**. Update `ALLOWED_HOSTS` to your Render URL and `CORS_ALLOWED_ORIGINS` to your Vercel frontend URL.

---

## Available Management Commands

```bash
python manage.py runserver        # Start dev server
python manage.py migrate          # Apply migrations
python manage.py makemigrations   # Create new migrations
python manage.py createsuperuser  # Create admin user
python manage.py shell            # Django interactive shell
```

---

## Related

- [JobTrackr Frontend](https://jobtraker.netlify.app/) — React + Vite frontend

---

## License

MIT
