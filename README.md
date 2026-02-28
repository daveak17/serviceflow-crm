# ServiceFlow CRM

Multi-tenant CRM SaaS platform for freelancers and small agencies.

## Tech Stack

**Backend:** Python, FastAPI, SQLAlchemy, MySQL, JWT
**Frontend:** HTML, CSS, Vanilla JavaScript, Chart.js
**Deployment:** Ubuntu VPS, Nginx, systemd, SSL

## Features

- User authentication (JWT + bcrypt)
- Client management
- Project and task management
- Time logging (billable/non-billable)
- Invoicing and payment tracking
- Analytics dashboard (in progress)

## Project Structure
`
serviceflow/
├── backend/     # FastAPI application
├── frontend/    # HTML/CSS/JS interface
└── README.md
`

## Setup
`ash
cd backend
python -m venv venv
source venv/bin/activate        # Linux/Mac
.\venv\Scripts\activate         # Windows
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your values
uvicorn main:app --reload
`

API docs: http://localhost:8000/docs

## Development Status

- [x] Phase 1 - Authentication (JWT, bcrypt)
- [x] Phase 2 - Core CRM (Clients, Projects, Tasks, Time Logs)
- [x] Phase 3 - Billing (Invoices, Payments)
- [ ] Phase 4 - Analytics Dashboard
- [ ] Phase 5 - Production Deployment
