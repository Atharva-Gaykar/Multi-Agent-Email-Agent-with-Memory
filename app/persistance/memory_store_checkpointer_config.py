from app.database.connection import pool
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.store.postgres import PostgresStore
from app.utils.embeddings import remote_embeddings

checkpointer = PostgresSaver(pool)


memory_store = PostgresStore(
    pool, 
    index={
        "dims": 384, 
        "embed": remote_embeddings,
        
        # FIX: Point exactly to the nested keys inside the stored JSON structure
        "fields": [
            "content.summary", 
            "content.user_email_id", 
            "content.receiver_email_id"
        ]
    }
)



