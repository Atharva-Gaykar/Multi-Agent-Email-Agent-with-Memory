from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
 
BASE_DIR = Path(__file__).resolve().parent.parent.parent
 
class Settings(BaseSettings):
    PROJECT_NAME: str = "Email Assistant Project"
    GROQ_API_KEY: str
    DB_URL_FOR_CHECKPOINTER_STORE: str

    GMAIL_CREDENTIALS_PATH: str = "credentials.json"
    GMAIL_TOKEN_PATH: str = "token.json"

    SECRET_KEY: str
    ALGORITHM: str

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    DB_URL_FOR_SQL_AL:str
 
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )
 
settings = Settings()


