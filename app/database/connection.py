from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings
from psycopg_pool import ConnectionPool



DB_URL_FOR_CHECKPOINTER_STORE=settings.DB_URL_FOR_CHECKPOINTER_STORE

pool = ConnectionPool(
    conninfo=DB_URL_FOR_CHECKPOINTER_STORE, 
    min_size=1, 
    max_size=10,
    kwargs={"autocommit": True} 
)


DB_URL_FOR_SQL_AL=settings.DB_URL_FOR_SQL_AL

engine = create_engine(
    DB_URL_FOR_SQL_AL, 
    echo=False, 
    pool_pre_ping=True, 
    pool_recycle=1800
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def get_session() -> Session:
    return SessionLocal()

DB_URL_FOR_CHECKPOINTER_STORE=settings.DB_URL_FOR_CHECKPOINTER_STORE

pool = ConnectionPool(
    conninfo=DB_URL_FOR_CHECKPOINTER_STORE, 
    min_size=1, 
    max_size=10,
    kwargs={"autocommit": True} 
)
