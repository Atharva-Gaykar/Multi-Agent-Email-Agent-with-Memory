from psycopg_pool import ConnectionPool
from langgraph.store.postgres import PostgresStore
from langgraph.checkpoint.postgres import PostgresSaver
from app.memory_store.embeddings import remote_embeddings

from app.core.config import settings


DB_URL_FOR_CHECKPOINTER_STORE=settings.DB_URL_FOR_CHECKPOINTER_STORE

pool = ConnectionPool(
    conninfo=DB_URL_FOR_CHECKPOINTER_STORE, 
    min_size=1, 
    max_size=10,
    kwargs={"autocommit": True} 
)

memory_store = PostgresStore(pool, index={"dims": 384, "embed": remote_embeddings})