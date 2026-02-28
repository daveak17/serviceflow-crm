from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.db.database import init_db
from app.api import auth, clients, projects, tasks, time_logs, invoices

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

STATIC_DIR = Path(__file__).resolve().parent.parent.parent / "frontend" / "static"
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

init_db()

app.include_router(auth.router)
app.include_router(clients.router)
app.include_router(projects.router)
app.include_router(tasks.router)
app.include_router(time_logs.router)
app.include_router(invoices.router)


@app.get("/health")
def health_check():
    return {
        "status": "running",
        "app": settings.APP_NAME,
        "env": settings.APP_ENV,
    }