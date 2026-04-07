from app.graph import graph
from app.database.connection import pool
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.store.postgres import PostgresStore
from app.utils.embeddings import remote_embeddings




checkpointer = PostgresSaver(pool)
memory_store = PostgresStore(pool, embeddings=remote_embeddings)


