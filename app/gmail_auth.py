import os
from pathlib import Path
from app.core.config import settings

# CREATE TEMP DIRECTORY

AUTH_DIR = Path("/tmp/google_auth")
AUTH_DIR.mkdir(parents=True, exist_ok=True)

# FULL FILE PATHS

CREDENTIALS_PATH = AUTH_DIR / "credentials.json"
TOKEN_PATH = AUTH_DIR / "token.json"

# CREATE FILES FROM HF SECRETS

if not CREDENTIALS_PATH.exists():
    CREDENTIALS_PATH.write_text(os.environ["GOOGLE_CREDENTIALS"])

if not TOKEN_PATH.exists():
    TOKEN_PATH.write_text(os.environ["GOOGLE_TOKEN"])

# GMAIL IMPORTS

from langchain_google_community.gmail.utils import (
    build_resource_service,
    get_gmail_credentials,
)

from langchain_google_community import GmailToolkit

# LOAD CREDENTIALS

credentials = get_gmail_credentials(
    token_file=str(TOKEN_PATH),
    scopes=["https://mail.google.com/"],
    client_sercret_file=str(CREDENTIALS_PATH),
)

# BUILD API RESOURCE

api_resource = build_resource_service(
    credentials=credentials
)

# TOOLKIT

gmail_toolkit = GmailToolkit(
    api_resource=api_resource
)