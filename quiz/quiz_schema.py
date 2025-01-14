from pydantic import BaseModel

class QuizCreate(BaseModel):
    topic: str
    question_count: int
    type: str

class QuizBase(BaseModel):
    quiz_number: int
    quiz_question: str
    quiz_answer: str
    quiz_type: str

class Quiz(QuizBase):
    quiz_id: int

    class Config:
        orm_mode = True

        from pydantic import BaseModel