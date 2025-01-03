from pydantic import BaseModel
from datetime import datetime

class RetryBase(BaseModel):
    user_id: int
    quiz_id: int
    is_correct: bool = False
    attempted_at: datetime = None

class RetryCreate(RetryBase):
    pass

class Retry(RetryBase):
    retry_id: int

    class Config:
        orm_mode = True
