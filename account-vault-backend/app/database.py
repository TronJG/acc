# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import DATABASE_URL

# Phân tích URL để quyết định connect_args
url = make_url(DATABASE_URL)

connect_args = {}
if url.get_backend_name().startswith("sqlite"):
    # SQLite (local dev): cần check_same_thread=False
    connect_args["check_same_thread"] = False
    # Với SQLite, sslmode không liên quan
# Với Postgres/Neon: không cần connect_args; sslmode đã có trên URL

engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args=connect_args,
    pool_pre_ping=True,  # tránh kết nối chết khi idle lâu (Render free hay sleep)
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def get_db():
    """Dependency cho mỗi request: mở/đóng session DB."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Tạo bảng (gọi lúc startup)."""
    # Import models để SQLAlchemy biết metadata
    from . import models  # noqa: F401
    Base.metadata.create_all(bind=engine)
