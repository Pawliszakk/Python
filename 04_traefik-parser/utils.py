from datetime import datetime

def from_microseconds_to_seconds(value):
        return round(value/1000000,2)

def from_seconds_to_microseconds(value):
        return value * 1_000_000

def parse_user_datetime(value):
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    raise ValueError(f"Invalid date format: {value}. Use YYYY-MM-DD or 'YYYY-MM-DD HH:MM'")