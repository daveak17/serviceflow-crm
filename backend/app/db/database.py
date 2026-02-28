from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=settings.DEBUG
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    from app.models import user      # noqa: F401
    from app.models import client    # noqa: F401
    from app.models import project   # noqa: F401
    from app.models import task      # noqa: F401
    from app.models import time_log  # noqa: F401
    from app.models import invoice   # noqa: F401
    Base.metadata.create_all(bind=engine)