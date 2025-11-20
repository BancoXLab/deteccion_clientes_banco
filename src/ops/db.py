from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import os

DB_URL = os.getenv("ALERTS_DB_URL")
if not DB_URL:
    # Prefer MySQL if available (docker compose sets env), fallback to sqlite
    mysql_user = os.getenv("MYSQL_USER")
    mysql_pass = os.getenv("MYSQL_PASSWORD")
    mysql_host = os.getenv("MYSQL_HOST", os.getenv("MYSQL_HOSTNAME", "mysql"))
    mysql_db = os.getenv("MYSQL_DATABASE")
    if mysql_user and mysql_pass and mysql_db:
        DB_URL = f"mysql+pymysql://{mysql_user}:{mysql_pass}@{mysql_host}:3306/{mysql_db}"
    else:
        DB_URL = os.getenv("ALERTS_DB_URL", "sqlite:///./alerts.db")

engine = create_engine(DB_URL, pool_pre_ping=True, connect_args={"check_same_thread": False} if DB_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Alert(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True, index=True)
    level = Column(String(32), index=True)
    message = Column(Text)
    extra = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)


class Metric(Base):
    __tablename__ = "metrics"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(128), index=True)
    value = Column(Float)
    ts = Column(DateTime, default=datetime.utcnow, index=True)


def init_db():
    Base.metadata.create_all(bind=engine)


def save_alert(level: str, message: str, extra: str = None):
    db = SessionLocal()
    try:
        a = Alert(level=level, message=message, extra=extra)
        db.add(a)
        db.commit()
        db.refresh(a)
        return a
    finally:
        db.close()


def save_metric(name: str, value: float):
    db = SessionLocal()
    try:
        m = Metric(name=name, value=value)
        db.add(m)
        db.commit()
        db.refresh(m)
        return m
    finally:
        db.close()
