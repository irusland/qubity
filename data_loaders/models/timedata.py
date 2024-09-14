from datetime import datetime
from pydantic import BaseModel, field_validator


class TimeData(BaseModel):
    timestamp: datetime
