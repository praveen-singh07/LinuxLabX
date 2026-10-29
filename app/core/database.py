import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# Load environment variables from .env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./linuxlabx.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)


# Let SQLAlchemy control SQLite transaction boundaries.
@event.listens_for(engine, "connect")
def configure_sqlite(dbapi_connection, connection_record):
    dbapi_connection.isolation_level = None


@event.listens_for(engine, "begin")
def begin_sqlite_transaction(connection):
    connection.exec_driver_sql("BEGIN")


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
