def get_username_from_email(email: str) -> str:
    if not email or "@" not in email:
        raise ValueError("Invalid email format")
    return email.split("@", 1)[0]