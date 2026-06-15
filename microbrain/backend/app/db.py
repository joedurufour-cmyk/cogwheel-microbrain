import os

from sqlalchemy import create_engine
from sqlalchemy import inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./microbrain_dev.db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg://", 1)
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    from app import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    ensure_lightweight_migrations()


def ensure_lightweight_migrations() -> None:
    inspector = inspect(engine)
    if "narrative_states" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("narrative_states")}
    additions = {
        "central_objects_json": "TEXT DEFAULT '[]'",
        "active_relations_json": "TEXT DEFAULT '[]'",
        "blocking_gap": "TEXT",
        "input_contract_json": "TEXT DEFAULT '{}'",
        "output_contract_json": "TEXT DEFAULT '{}'",
        "resolved_gaps_json": "TEXT DEFAULT '[]'",
        "active_domain": "TEXT",
        "anticipation_gaps_json": "TEXT DEFAULT '[]'",
    }
    with engine.begin() as connection:
        for column, ddl_type in additions.items():
            if column not in columns:
                connection.execute(text(f"ALTER TABLE narrative_states ADD COLUMN {column} {ddl_type}"))
