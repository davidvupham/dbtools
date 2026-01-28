def is_valid_username(username: str) -> bool:
    if not username:
        return False
    if " " in username:
        return False
    if len(username) < 3:
        return False
    return True
