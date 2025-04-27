from datetime import datetime

def is_int(value) -> bool:
    try:
        int(value)
        return True
    except (ValueError, TypeError):
        return False

def is_valid_date(s: str, fmt: str = "%Y-%m-%d") -> bool:
    try:
        datetime.strptime(s, fmt)
        return True
    except ValueError:
        return False