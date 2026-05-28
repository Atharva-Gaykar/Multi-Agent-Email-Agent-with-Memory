import os
from pathlib import Path
from app.core.config import settings

AUTH_DIR = Path("/tmp/google_auth")
AUTH_DIR.mkdir(parents=True, exist_ok=True)


CREDENTIALS_PATH = AUTH_DIR / "credentials.json"
TOKEN_PATH = AUTH_DIR / "token.json"

if "GOOGLE_CREDENTIALS" in os.environ:
    CREDENTIALS_PATH.write_text(os.environ["GOOGLE_CREDENTIALS"])
else:
    raise ValueError("GOOGLE_CREDENTIALS secret is missing from environment variables!")

if "GOOGLE_TOKEN" in os.environ:
    TOKEN_PATH.write_text(os.environ["GOOGLE_TOKEN"])
else:
    raise ValueError("GOOGLE_TOKEN secret is missing from environment variables!")


from langchain_google_community.gmail.utils import (
    build_resource_service,
    get_gmail_credentials,
)
from langchain_google_community import GmailToolkit

credentials = get_gmail_credentials( 
    token_file=str(TOKEN_PATH.resolve()),
    scopes=["https://mail.google.com/"],
    client_sercret_file=str(CREDENTIALS_PATH.resolve()),  
)

# BUILD API RESOURCE
api_resource = build_resource_service(
    credentials=credentials
)

# TOOLKIT
gmail_toolkit = GmailToolkit(
    api_resource=api_resource
)


