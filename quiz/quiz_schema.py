from pydantic import BaseModel

# 요청 데이터 스키마
class QuizCreate(BaseModel):
    topic: str  # 퀴즈 주제
    question_count: int  # 생성할 퀴즈 개수
    type: str  # 퀴즈 타입 (예: "객관식", "주관식")

# 응답 데이터 스키마
class QuizResponse(BaseModel):
    id: int
    number: int
    question: str
    answer: str
    type: str

    class Config:
        orm_mode = True