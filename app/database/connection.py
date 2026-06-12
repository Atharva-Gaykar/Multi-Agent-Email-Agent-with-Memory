from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings
from psycopg_pool import ConnectionPool
from contextlib import contextmanager


DB_URL_FOR_CHECKPOINTER_STORE=settings.DB_URL_FOR_CHECKPOINTER_STORE


pool = ConnectionPool(
    conninfo=DB_URL_FOR_CHECKPOINTER_STORE,
    min_size=1,
    max_size=10,
    check=ConnectionPool.check_connection,
    max_idle=300,
    kwargs={"autocommit": True,"sslmode": "require"}
)

# sslmode=require means that our application will only connect to the database if a secure, encrypted connection can be established. 


DB_URL_FOR_SQL_AL=settings.DB_URL_FOR_SQL_AL


# pool_pre_ping=True: It checks if a connection is still alive before using it. If it's dead, it recycles it so the app doesn't crash.
# pool_recycle=300: It closes and recreates connections every 5 minutes (300 seconds) to prevent stale connections.

engine = create_engine(
    DB_URL_FOR_SQL_AL, 
    pool_pre_ping=True, 
    pool_recycle=300
)



# This is a factory that generates individual database sessions
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# This creates a session factory. We set autoflush=False and autocommit=False because we want manual control over when data is saved (committed) to the database, which prevents accidental or premature changes.


def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


