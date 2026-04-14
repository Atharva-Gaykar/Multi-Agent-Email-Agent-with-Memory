


def parse_interrupt(final_state: dict):
    if "__interrupt__" not in final_state:
        return None

    interrupt_state = final_state["__interrupt__"]
    if not interrupt_state:
        return None

    interrupt = interrupt_state[0]
    value = getattr(interrupt, "value", {}) or {}

    return {
        "action": value.get("action"),
        "data": value.get("data", {})
    }