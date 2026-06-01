import re
from datetime import datetime


def format_currency(amount):
    try:
        return f"৳ {float(amount):,.2f}"
    except (ValueError, TypeError):
        return "৳ 0.00"


def format_datetime(dt):
    if isinstance(dt, datetime):
        return dt.strftime("%d %b %Y, %I:%M %p")
    return str(dt) if dt else "—"


def format_date(dt):
    if isinstance(dt, datetime):
        return dt.strftime("%d %b %Y")
    return str(dt) if dt else "—"


def validate_phone(phone: str) -> bool:
    return bool(re.match(r"^01[3-9]\d{8}$", phone.strip()))


def validate_email(email: str) -> bool:
    return bool(re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email.strip()))


def validate_password(password: str) -> bool:
    """Min 8 chars, 1 uppercase, 1 digit."""
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"\d", password):
        return False
    return True