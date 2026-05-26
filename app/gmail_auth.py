from app.core.config import settings
from langchain_google_community.gmail.utils import (
    build_resource_service,
    get_gmail_credentials,
)

from langchain_google_community import GmailToolkit
credentials = get_gmail_credentials(
    token_file=settings.GMAIL_TOKEN_PATH,
    scopes=["https://mail.google.com/"],
    client_sercret_file=settings.GMAIL_CREDENTIALS_PATH,
)

api_resource = build_resource_service(
    credentials=credentials
)

gmail_toolkit = GmailToolkit(
    api_resource=api_resource
)