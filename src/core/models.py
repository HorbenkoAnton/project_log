from pydantic import BaseModel

class LogEntry(BaseModel):
    level: str
    message: str
    service: str
    timestamp: float

