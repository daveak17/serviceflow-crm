from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.core.config import settings
from app.db.database import init_db
from app.api import auth, clients, projects, tasks, time_logs, invoices, analytics

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

BASE_DIR = Path(__file__).resolve().parent.parent.parent
STATIC_DIR = BASE_DIR / "frontend" / "static"
TEMPLATES_DIR = BASE_DIR / "frontend" / "templates"

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

init_db()

app.include_router(auth.router)
app.include_router(clients.router)
app.include_router(projects.router)
app.include_router(tasks.router)
app.include_router(time_logs.router)
app.include_router(invoices.router)
app.include_router(analytics.router)


@app.get("/health")
def health_check():
    return {
        "status": "running",
        "app": settings.APP_NAME,
        "env": settings.APP_ENV,
    }


@app.get("/{full_path:path}")
def serve_frontend(full_path: str):
    if (full_path.startswith("api/") or
        full_path in ("docs", "redoc", "openapi.json") or
        full_path.startswith("static/")):
        raise HTTPException(status_code=404)
    index = TEMPLATES_DIR / "index.html"
    return FileResponse(str(index))