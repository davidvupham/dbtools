import time


def slow_api_call(user_id):
    """Simulates a slow network request."""
    # In a real test, if this sleep happens, we failed to mock!
    time.sleep(2)
    return {"id": user_id, "active": True}

def get_user_status(user_id):
    """The function we want to test."""
    data = slow_api_call(user_id)
    if data["active"]:
        return "Active User"
    return "Inactive"
