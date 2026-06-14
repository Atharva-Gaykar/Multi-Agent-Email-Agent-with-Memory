
import base64


def encode_email_for_namespace(email: str) -> str:
    """Encodes email to a safe string without periods."""
    return base64.b32encode(email.lower().encode("utf-8")).decode("utf-8").replace("=", "")