from pydantic import BaseModel
from typing import List

class QuizCreate(BaseModel):
    question: str
    answer: str
    options: List[str]
    category: str = None

class QuizResponse(BaseModel):
    quiz_id: int
    question: str
    answer: str
    options: List[str]
    category: str