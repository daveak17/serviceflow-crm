# ServiceFlow CRM

ServiceFlow CRM is a multi-user SaaS CRM platform built for freelancers and small agencies.

The goal of the system is to provide structured client management, project tracking, invoicing, payments, and revenue analytics inside a secure, production-ready web application.

---

## Architecture

This project follows a clean backend/frontend separation.

### Backend
- Python
- FastAPI
- SQLAlchemy ORM
- MySQL / MariaDB
- JWT authentication (python-jose)
- Password hashing (bcrypt via passlib)
- Pydantic validation

### Frontend
- HTML
- CSS
- Vanilla JavaScript
- Fetch API
- Chart.js (for analytics dashboard)

---

## Current Status

### Implemented
- User registration
- User login with JWT authentication
- Password hashing with bcrypt
- Protected routes
- Database connection using SQLAlchemy
- Relational schema foundation
- Service layer architecture

### In Progress
- Clients CRUD
- Projects CRUD
- Tasks management
- Time tracking
- Invoicing system
- Payment tracking
- Revenue analytics dashboard

---

## Project Structure

```
serviceflow-crm
│
├── backend
│   ├── app
│   ├── scripts
│   ├── requirements.txt
│   └── .env.example
│
├── frontend
│
├── logs
│
├── .gitignore
└── README.md
```

---

## Setup

### 1. Clone the repository

```
git clone https://github.com/daveak17/serviceflow-crm.git
cd serviceflow-crm
```

---

## Backend Setup (Windows PowerShell)

```
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

---

## Backend Setup (Linux / macOS)

```
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

---

## API Documentation

Once running, open:

```
http://localhost:8000/docs
```

Swagger UI will be available automatically.

---

## Environment Variables

Create a `.env` file inside the backend folder based on `.env.example`.

Example:

```
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/serviceflow
JWT_SECRET_KEY=change_me
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

Never commit real secrets to the repository.

---

## Security Features

- Bcrypt password hashing
- JWT access tokens
- Token expiration validation
- User ownership validation for protected resources
- Environment variable configuration
- Relational integrity via foreign keys

---

## Development Approach

The project follows structured commits and modular development:

- Models layer
- Schemas layer
- Services layer
- API routers
- Authentication dependency injection

Each feature is implemented incrementally and version controlled with meaningful commit messages.

---

## Deployment Target

Planned production environment:

- Ubuntu VPS
- Nginx reverse proxy
- systemd service
- SSL certificate
- Environment-based configuration

---

## Author

David Akoda  
Junior Software Engineer  
Focused on full stack development, SaaS systems, and production-ready backend architecture.

---

## Vision

By completion, ServiceFlow CRM will be a fully functional multi tenant CRM SaaS platform with:

- Secure authentication
- Client and project management
- Automated invoicing
- Payment tracking
- Revenue analytics dashboard
- Production deployment on Linux VPS
