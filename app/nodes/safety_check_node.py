import httpx
from typing import Any
from app.state.state import EmailAgentState


SAFETY_API_URL = "https://gaykar-classifyemail.hf.space/predict"

def safety_classifier_node(state: EmailAgentState) -> dict:
    payload = {
        "subject": state["sender_subject"],
        "body":    state["sender_email_body"],
    }
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.post(SAFETY_API_URL, json=payload)
            response.raise_for_status()
            result = response.json()

        prediction    = result.get("prediction", "UNSAFE").upper()
        confidence    = result.get("confidence", "0.00%")
        url_count     = result.get("url_count", 0)
        is_safe       = prediction == "SAFE"
        safety_reason = None
        if not is_safe:
            safety_reason = (
                f"Classified as {prediction} "
                f"(confidence: {confidence}, urls found: {url_count})"
            )
        return {"is_safe": is_safe, "safety_reason": safety_reason}

    except httpx.TimeoutException:
        return {"is_safe": False, "safety_reason": "Safety API timed out"}
    except httpx.HTTPStatusError as e:
        return {"is_safe": False, "safety_reason": f"API error {e.response.status_code}"}
    


def after_safety(state: EmailAgentState) -> str:
    if not state["is_safe"]:
        return "unsafe_emails_node"
    return "triage_node"
