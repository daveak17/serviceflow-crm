# ServiceFlow CRM

A multi-tenant CRM SaaS platform for freelancers and small agencies. Built with FastAPI, MySQL, and vanilla JavaScript. Deployed on Railway.

**Live Demo:** https://serviceflow-crm-production.up.railway.app

```
Demo credentials
Email:    demo@serviceflow.com
Password: demo1234
```

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

---

## Features

**Authentication**
- JWT-based login and registration
- bcrypt password hashing
- Protected routes — users only access their own data

**Client Management**
- Create, edit, and delete clients
- Store contact details and company information
- Search and filter

**Project Management**
- Link projects to clients
- Track status: Active, On Hold, Completed
- Set budgets and deadlines

**Task Management**
- Kanban-style columns: To Do, In Progress, Done
- Priority levels: High, Medium, Low
- Filter by project and priority

**Time Tracking**
- Log billable and non-billable hours per project
- Set hourly rates per entry
- View total hours across projects

**Invoicing**
- Create invoices with multiple line items
- Apply tax rates — totals calculated automatically
- Status workflow: Draft → Sent → Paid
- Expandable payment history per invoice
- Balance due calculated after partial payments

**Payment Tracking**
- Record full or partial payments against invoices
- Payment modal pre-fills the remaining balance due
- Visual indicators: Paid in full / amount due

**Analytics Dashboard**
- Total Invoiced, Collected, Outstanding, Net Income
- Monthly revenue bar chart (last 6 months)
- Top clients by invoiced and collected amounts
- Outstanding invoices list

---

## Tech Stack

**Backend**
- Python 3.13
- FastAPI + Uvicorn
- SQLAlchemy ORM
- PyMySQL
- Pydantic v2
- passlib + bcrypt
- python-jose (JWT)

**Database**
- MySQL (Railway managed)
- Relational schema with foreign keys enforced
- Multi-tenant — all queries scoped by user_id

**Frontend**
- HTML, CSS, Vanilla JavaScript
- Fetch API for all backend communication
- Chart.js for analytics visualisations
- Responsive — mobile and desktop

**Deployment**
- Railway (backend + MySQL)
- Environment variables for all secrets
- Auto-deploy from GitHub main branch

---

## Project Structure

```
serviceflow-crm/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes/          # auth, clients, projects, tasks,
│   │   │                        # timelogs, invoices, analytics
│   │   ├── db/
│   │   │   └── database.py      # SQLAlchemy engine and session
│   │   ├── models/              # SQLAlchemy ORM models
│   │   ├── schemas/             # Pydantic request/response schemas
│   │   ├── services/            # Business logic (analytics_service)
│   │   └── core/
│   │       ├── config.py        # Settings from environment
│   │       └── security.py      # JWT and password hashing
│   ├── seed_data.py             # Demo data seeder
│   └── main.py                  # FastAPI app entry point
├── frontend/
│   ├── templates/
│   │   └── index.html           # Single page application shell
│   └── static/
│       ├── css/
│       │   └── app.css          # All styles, responsive breakpoints
│       ├── js/
│       │   ├── api.js           # Fetch wrapper for all API calls
│       │   ├── app.js           # App init, routing, auth state
│       │   ├── auth.js          # Login and register forms
│       │   ├── dashboard.js     # Analytics and charts
│       │   ├── clients.js
│       │   ├── projects.js
│       │   ├── tasks.js
│       │   ├── timelogs.js
│       │   └── invoices.js      # Invoices and payment recording
│       └── images/
├── docs/
│   └── screenshots/
└── README.md
```

---

## Database Schema

```
users
  └── clients
  └── projects
        └── tasks
        └── time_logs
  └── invoices
        └── invoice_items
        └── payments
```

All tables include `user_id` foreign key. No cross-tenant data access is possible at the query level.

---

## Local Setup

**Requirements**
- Python 3.10+
- MySQL running locally

**Steps**

```bash
# Clone
git clone https://github.com/daveak17/serviceflow-crm.git
cd serviceflow-crm/backend

# Create virtual environment
python -m venv .venv

# Activate (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# Activate (macOS/Linux)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

Create a `.env` file in `backend/`:

```env
DATABASE_URL=mysql+pymysql://your_user:your_password@localhost:3306/serviceflow_db
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
DEBUG=true
```

```bash
# Create database tables and run
cd backend
python main.py

# Seed demo data (optional)
python seed_data.py
```

App runs at `http://localhost:8000`

---

## Deployment (Railway)

1. Push repo to GitHub
2. Create a new Railway project
3. Add a MySQL service
4. Deploy from GitHub — Railway auto-detects Python
5. Set environment variables in Railway Variables tab:
   - `DATABASE_URL` — from Railway MySQL `MYSQL_URL`
   - `SECRET_KEY` — any long random string
   - `ALGORITHM=HS256`
   - `ACCESS_TOKEN_EXPIRE_MINUTES=60`
6. Railway deploys on every push to `main`

---

## Security

- Passwords hashed with bcrypt (cost factor 12)
- JWT tokens with configurable expiry
- All API routes require `Authorization: Bearer <token>`
- Every database query filters by authenticated `user_id`
- No secrets in source code — all via environment variables

---

## Author

David — Junior Software Engineer  
GitHub: https://github.com/daveak17