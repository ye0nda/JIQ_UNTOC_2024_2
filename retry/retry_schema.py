from pydantic import BaseModel
from datetime import datetime

class RetryBase(BaseModel):
    retry_id: int
    retry_question: str
    user_answer: str
    correct_answer: str
    is_correct: bool = False

class RetryCreate(RetryBase):
    pass

class Retry(RetryBase):
    retry_id: int

    class Config:
        orm_mode = True
