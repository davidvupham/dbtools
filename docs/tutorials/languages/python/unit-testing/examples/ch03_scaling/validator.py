def is_valid_username(username: str) -> bool:
    if not username:
        return False
    if " " in username:
        return False
    return len(username) >= 3
