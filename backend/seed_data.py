"""
ServiceFlow CRM — Demo Data Seeder
Run: python seed_data.py
Creates one demo user with realistic data across all tables.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import date, datetime, timedelta
from decimal import Decimal
import bcrypt
from sqlalchemy.orm import Session
from app.db.database import SessionLocal, init_db
from app.models.user import User
from app.models.client import Client
from app.models.project import Project
from app.models.task import Task
from app.models.time_log import TimeLog
from app.models.invoice import Invoice, InvoiceItem, Payment, InvoiceStatus


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(12)).decode('utf-8')


def seed(db: Session):
    # ── Check if demo user already exists ──
    existing = db.query(User).filter(User.email == "demo@serviceflow.com").first()
    if existing:
        print("Demo user already exists. Skipping seed.")
        print("Login: demo@serviceflow.com / demo1234")
        return

    print("Seeding demo data...")

    # ── User ──
    user = User(
        full_name="Alex Rivera",
        email="demo@serviceflow.com",
        hashed_password=hash_password("demo1234"),
        is_active=True,
        is_verified=True,
    )
    db.add(user)
    db.flush()
    uid = user.id
    print(f"  Created user: {user.email}")

    # ── Clients ──
    clients_data = [
        {"name": "Bright Digital", "company": "Bright Digital Ltd", "email": "hello@brightdigital.com", "phone": "+1 415 555 0101"},
        {"name": "Nova Analytics", "company": "Nova Analytics Inc", "email": "contact@novaanalytics.io", "phone": "+1 212 555 0182"},
        {"name": "Greenleaf Studio", "company": "Greenleaf Studio LLC", "email": "studio@greenleaf.co", "phone": "+1 310 555 0134"},
        {"name": "Summit Ventures", "company": "Summit Ventures Group", "email": "info@summitventures.com", "phone": "+1 512 555 0167"},
        {"name": "Pixel & Co", "company": "Pixel & Co Design", "email": "team@pixelco.design", "phone": "+1 617 555 0193"},
    ]
    clients = []
    for cd in clients_data:
        c = Client(**cd, user_id=uid)
        db.add(c)
        clients.append(c)
    db.flush()
    print(f"  Created {len(clients)} clients")

    # ── Projects ──
    today = date.today()
    projects_data = [
        {"name": "Brand Identity Redesign", "client": clients[0], "status": "completed", "budget": 8500, "description": "Full rebrand including logo, color system, and style guide", "deadline": today - timedelta(days=30)},
        {"name": "E-commerce Platform", "client": clients[1], "status": "active", "budget": 24000, "description": "Custom Shopify build with analytics integration", "deadline": today + timedelta(days=45)},
        {"name": "Mobile App MVP", "client": clients[2], "status": "active", "budget": 18000, "description": "iOS and Android app for studio booking system", "deadline": today + timedelta(days=90)},
        {"name": "SEO & Content Strategy", "client": clients[3], "status": "on_hold", "budget": 5500, "description": "12-month SEO roadmap and content calendar", "deadline": today + timedelta(days=60)},
        {"name": "Dashboard UI Kit", "client": clients[4], "status": "active", "budget": 6000, "description": "Figma component library and design system", "deadline": today + timedelta(days=20)},
        {"name": "API Integration", "client": clients[0], "status": "completed", "budget": 4200, "description": "Third-party payment and shipping API integration", "deadline": today - timedelta(days=60)},
    ]
    projects = []
    for pd in projects_data:
        client = pd.pop("client")
        p = Project(**pd, client_id=client.id, user_id=uid)
        db.add(p)
        projects.append(p)
    db.flush()
    print(f"  Created {len(projects)} projects")

    # ── Tasks ──
    tasks_data = [
        # E-commerce Platform
        {"title": "Set up Shopify environment", "project": projects[1], "status": "done", "priority": "high", "due_date": today - timedelta(days=10)},
        {"title": "Build product catalogue", "project": projects[1], "status": "done", "priority": "high", "due_date": today - timedelta(days=5)},
        {"title": "Payment gateway integration", "project": projects[1], "status": "in_progress", "priority": "high", "due_date": today + timedelta(days=7)},
        {"title": "Analytics dashboard setup", "project": projects[1], "status": "todo", "priority": "medium", "due_date": today + timedelta(days=20)},
        {"title": "User testing and QA", "project": projects[1], "status": "todo", "priority": "medium", "due_date": today + timedelta(days=35)},
        # Mobile App
        {"title": "Wireframes and user flows", "project": projects[2], "status": "done", "priority": "high", "due_date": today - timedelta(days=20)},
        {"title": "UI design — booking screen", "project": projects[2], "status": "in_progress", "priority": "high", "due_date": today + timedelta(days=10)},
        {"title": "Backend API endpoints", "project": projects[2], "status": "in_progress", "priority": "high", "due_date": today + timedelta(days=15)},
        {"title": "Push notification system", "project": projects[2], "status": "todo", "priority": "low", "due_date": today + timedelta(days=50)},
        # Dashboard UI Kit
        {"title": "Define component architecture", "project": projects[4], "status": "done", "priority": "high", "due_date": today - timedelta(days=3)},
        {"title": "Build core components", "project": projects[4], "status": "in_progress", "priority": "high", "due_date": today + timedelta(days=10)},
        {"title": "Documentation and handoff", "project": projects[4], "status": "todo", "priority": "medium", "due_date": today + timedelta(days=18)},
    ]
    tasks = []
    for td in tasks_data:
        project = td.pop("project")
        t = Task(**td, project_id=project.id, user_id=uid)
        db.add(t)
        tasks.append(t)
    db.flush()
    print(f"  Created {len(tasks)} tasks")

    # ── Time Logs ──
    timelogs_data = [
        {"project": projects[0], "hours": 12, "hourly_rate": 95, "is_billable": True, "description": "Brand strategy workshop", "logged_date": today - timedelta(days=45)},
        {"project": projects[0], "hours": 20, "hourly_rate": 95, "is_billable": True, "description": "Logo design and iterations", "logged_date": today - timedelta(days=40)},
        {"project": projects[0], "hours": 8, "hourly_rate": 95, "is_billable": True, "description": "Style guide document", "logged_date": today - timedelta(days=35)},
        {"project": projects[1], "hours": 6, "hourly_rate": 110, "is_billable": True, "description": "Shopify theme setup", "logged_date": today - timedelta(days=12)},
        {"project": projects[1], "hours": 8, "hourly_rate": 110, "is_billable": True, "description": "Product catalog build", "logged_date": today - timedelta(days=7)},
        {"project": projects[1], "hours": 2, "hourly_rate": None, "is_billable": False, "description": "Client calls and project management", "logged_date": today - timedelta(days=5)},
        {"project": projects[2], "hours": 10, "hourly_rate": 100, "is_billable": True, "description": "Wireframe design", "logged_date": today - timedelta(days=22)},
        {"project": projects[2], "hours": 7, "hourly_rate": 100, "is_billable": True, "description": "UI screens — booking flow", "logged_date": today - timedelta(days=3)},
        {"project": projects[4], "hours": 5, "hourly_rate": 90, "is_billable": True, "description": "Component architecture planning", "logged_date": today - timedelta(days=4)},
        {"project": projects[4], "hours": 8, "hourly_rate": 90, "is_billable": True, "description": "Core component build", "logged_date": today - timedelta(days=1)},
        {"project": projects[5], "hours": 14, "hourly_rate": 105, "is_billable": True, "description": "API integration and testing", "logged_date": today - timedelta(days=65)},
    ]
    for tld in timelogs_data:
        project = tld.pop("project")
        logged_date = tld.pop("logged_date")
        tl = TimeLog(
            **tld,
            project_id=project.id,
            user_id=uid,
            logged_date=datetime.combine(logged_date, datetime.min.time())
        )
        db.add(tl)
    db.flush()
    print(f"  Created {len(timelogs_data)} time logs")

    # ── Invoices ──
    def make_invoice(db, inv_num, client, project, items_data, tax_rate, status, issue_days_ago, due_days_from_issue, payments=[]):
        issue = today - timedelta(days=issue_days_ago)
        due = issue + timedelta(days=due_days_from_issue)
        inv = Invoice(
            user_id=uid,
            client_id=client.id,
            invoice_number=inv_num,
            status=status,
            issue_date=issue,
            due_date=due,
            tax_rate=tax_rate,
        )
        db.add(inv)
        db.flush()

        subtotal = Decimal("0")
        for item in items_data:
            s = Decimal(str(item["quantity"])) * Decimal(str(item["unit_price"]))
            ii = InvoiceItem(
                invoice_id=inv.id,
                description=item["description"],
                quantity=Decimal(str(item["quantity"])),
                unit_price=Decimal(str(item["unit_price"])),
                subtotal=s.quantize(Decimal("0.01"))
            )
            db.add(ii)
            subtotal += s

        tax = (subtotal * Decimal(str(tax_rate)) / 100).quantize(Decimal("0.01"))
        total = subtotal + tax

        for pay in payments:
            p = Payment(
                invoice_id=inv.id,
                user_id=uid,
                amount=Decimal(str(pay["amount"])),
                payment_date=today - timedelta(days=pay["days_ago"])
            )
            db.add(p)

        return inv

    make_invoice(db, "INV-2025-001", clients[0], projects[5],
        [{"description": "API Integration — 14 hours @ $105/hr", "quantity": 14, "unit_price": 105},
         {"description": "Testing and documentation", "quantity": 4, "unit_price": 85}],
        tax_rate=10, status=InvoiceStatus.paid,
        issue_days_ago=70, due_days_from_issue=30,
        payments=[{"amount": 1820, "days_ago": 50}])

    make_invoice(db, "INV-2025-002", clients[0], projects[0],
        [{"description": "Brand Strategy Workshop — 12hrs", "quantity": 12, "unit_price": 95},
         {"description": "Logo Design & Iterations — 20hrs", "quantity": 20, "unit_price": 95},
         {"description": "Style Guide Document — 8hrs", "quantity": 8, "unit_price": 95}],
        tax_rate=10, status=InvoiceStatus.paid,
        issue_days_ago=38, due_days_from_issue=30,
        payments=[{"amount": 2000, "days_ago": 30}, {"amount": 2090, "days_ago": 15}])

    make_invoice(db, "INV-2026-001", clients[1], projects[1],
        [{"description": "Shopify Setup & Configuration", "quantity": 6, "unit_price": 110},
         {"description": "Product Catalogue Build", "quantity": 8, "unit_price": 110}],
        tax_rate=8, status=InvoiceStatus.paid,
        issue_days_ago=14, due_days_from_issue=14,
        payments=[{"amount": 1555.2, "days_ago": 5}])

    make_invoice(db, "INV-2026-002", clients[2], projects[2],
        [{"description": "Wireframes & User Flows — 10hrs", "quantity": 10, "unit_price": 100},
         {"description": "UI Design Booking Screen — 7hrs", "quantity": 7, "unit_price": 100}],
        tax_rate=0, status=InvoiceStatus.sent,
        issue_days_ago=5, due_days_from_issue=30)

    make_invoice(db, "INV-2026-003", clients[4], projects[4],
        [{"description": "Component Architecture — 5hrs", "quantity": 5, "unit_price": 90},
         {"description": "Core Component Build — 8hrs", "quantity": 8, "unit_price": 90}],
        tax_rate=0, status=InvoiceStatus.sent,
        issue_days_ago=2, due_days_from_issue=21)

    make_invoice(db, "INV-2026-004", clients[3], projects[3],
        [{"description": "SEO Audit and Strategy Document", "quantity": 1, "unit_price": 2500},
         {"description": "Content Calendar — 3 months", "quantity": 1, "unit_price": 1200}],
        tax_rate=0, status=InvoiceStatus.draft,
        issue_days_ago=1, due_days_from_issue=30)

    db.commit()
    print(f"  Created 6 invoices with payments")
    print()
    print("=" * 45)
    print("  Seed complete.")
    print("  Login: demo@serviceflow.com")
    print("  Password: demo1234")
    print("=" * 45)


if __name__ == "__main__":
    init_db()
    db = SessionLocal()
    try:
        seed(db)
    finally:
        db.close()