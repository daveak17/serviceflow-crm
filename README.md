# ServiceFlow CRM

A full-stack multi-tenant CRM SaaS platform built for freelancers and small agencies.

ServiceFlow provides structured client management, project tracking, time logging, invoicing, payment recording, and a live revenue analytics dashboard — inside a secure, production-deployed web application.

**Live Demo:** https://serviceflow-crm-production.up.railway.app  
**Demo Login:** demo@serviceflow.com / demo1234

---

## Features

- **Authentication** — JWT-based login and registration with bcrypt password hashing
- **Clients** — Full CRUD with search and filtering
- **Projects** — Track status, budget, deadlines, and client assignments
- **Tasks** — Kanban-style board with priority levels and status columns
- **Time Logs** — Billable and non-billable hours with hourly rate tracking
- **Invoicing** — Line items, tax rate, status workflow (draft → sent → paid/overdue), duplicate protection
- **Payments** — Record payments against invoices with automatic balance calculation
- **Analytics Dashboard** — Revenue summary, monthly breakdown, top clients, project status distribution, outstanding invoices
- **Multi-tenant** — Each user only accesses their own data enforced at every layer
- **Responsive UI** — Full desktop sidebar layout + mobile header with slide-out navigation and FAB quick actions

---

## Screenshots

### Login
![Login](docs/screenshots/01-login.png)

### Dashboard
![Dashboard](docs/screenshots/02-dashboard.png)

![Dashboard Bottom](docs/screenshots/03-dashboard-bottom.png)

### Clients
![Clients](docs/screenshots/04-clients.png)

### Projects
![Projects](docs/screenshots/05-projects.png)

### Tasks
![Tasks](docs/screenshots/06-tasks.png)

### Time Logs
![Time Logs](docs/screenshots/07-timelogs.png)

### Invoices
![Invoices](docs/screenshots/08-invoices.png)

---

## Architecture

```
serviceflow-crm/
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI routers
│   │   ├── core/         # Config, JWT, security
│   │   ├── db/           # Database connection, session
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Pydantic validation schemas
│   │   ├── services/     # Business logic layer
│   │   └── main.py
│   ├── seed_data.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   └── templates/
│       └── index.html
├── Procfile
├── requirements.txt
└── README.md
```

### Backend Stack
- **Python** + **FastAPI** + **Uvicorn**
- **SQLAlchemy ORM** with relational schema and foreign key enforcement
- **MySQL** database
- **JWT authentication** via python-jose
- **bcrypt** password hashing via passlib
- **Pydantic** request/response validation

### Frontend Stack
- Vanilla **HTML**, **CSS**, **JavaScript**
- **Fetch API** for all HTTP communication
- **Chart.js** for analytics charts
- Single-page application served directly from FastAPI

### Architecture Patterns
- Service layer returning `(result, error)` tuples for clean error handling
- Ownership validation at every endpoint — users cannot access other users' data
- Pydantic schemas enforce input validation before reaching the database
- SQLAlchemy models with enums for status fields

---

## Local Setup

### Prerequisites
- Python 3.10+
- MySQL running locally

### 1. Clone the repository
```bash
git clone https://github.com/daveak17/serviceflow-crm.git
cd serviceflow-crm
```

### 2. Backend setup (Windows PowerShell)
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

### 2. Backend setup (Linux / macOS)
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### 3. Configure environment variables
Edit `backend/.env`:
```
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/serviceflow_db
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
APP_NAME=ServiceFlow CRM
APP_ENV=development
DEBUG=True
ALLOWED_ORIGINS=http://localhost:8000
```

### 4. Run the application
```bash
cd backend
uvicorn app.main:app --reload
```

Open: http://localhost:8000

### 5. Seed demo data (optional)
```bash
cd backend
python seed_data.py
```

Demo credentials: `demo@serviceflow.com` / `demo1234`

---

## API Documentation

Swagger UI available at:
```
http://localhost:8000/docs
```

All protected endpoints require a Bearer token in the Authorization header.

---

## Security

- Passwords hashed with bcrypt (never stored in plain text)
- JWT tokens with configurable expiry
- Every protected endpoint validates token and user ownership
- Cross-user data access prevented at the service layer
- Secrets managed via environment variables (never committed)
- `UniqueConstraint` on invoice numbers with 409 conflict response

---

## Deployment

Deployed on **Railway** with a managed MySQL database.

- FastAPI app served via Uvicorn on dynamic `$PORT`
- MySQL 9.4 on Railway internal network
- Environment variables configured via Railway dashboard
- Auto-deploy on push to `main` branch via GitHub integration

---

## Author

**David Akoda**  
Junior Software Engineer — full-stack development, SaaS systems, production-ready backend architecture.

GitHub: https://github.com/daveak17