from pydantic import BaseModel


class DateDuration(BaseModel):
    fiscal: str
    quarter: str
