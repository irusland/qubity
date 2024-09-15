from datetime import datetime, timezone


def to_timestamp(date: datetime) -> int:
    return int(date.timestamp() * 1000)


def to_minute_timeframe(dt, interval=5):
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    dt = dt.replace(second=0, microsecond=0)
    minute = (dt.minute // interval) * interval
    dt = dt.replace(minute=minute)
    return dt
