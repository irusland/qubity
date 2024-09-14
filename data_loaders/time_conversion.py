from datetime import datetime


def to_timestamp(date: datetime) -> int:
    return int(date.timestamp() * 1000)
