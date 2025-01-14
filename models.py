from sqlalchemy import Column, Integer, String, Boolean, DateTime
from database import FolderBase, QuizBase, RetryBase
from datetime import datetime

# Retry 테이블
class Retry(RetryBase):
    __tablename__ = "retry_attempts"
    retry_id = Column(Integer, primary_key=True, index=True) # 퀴즈 아이디랑 같게게
    quiz_id = Column(Integer)
    user_answer = Column(String(255), nullable=False) # 사용자가 제출한 답변
    correct_answer = Column(String(255), nullable=False) # 정답
    retry_question = Column(String(255), nullable=False) # 질문 내용
    is_correct = Column(Boolean, default=False) # 정답 여부 (default: False)
    attempted_at = Column(DateTime, default=datetime.utcnow) # 시도한 시간

# Folder 테이블
class Folder(FolderBase):
    __tablename__ = "folder"
    folder_id = Column(Integer, primary_key=True, index=True)
    folder_name = Column(String(255), nullable=False)

# Quiz 테이블
class Quiz(QuizBase):
    __tablename__ = "quizzes"
    quiz_id = Column(Integer, primary_key=True, index=True, autoincrement=True)  # autoincrement 추가
    quiz_number = Column(Integer, nullable=False)
    quiz_question = Column(String(255), nullable=False)
    quiz_answer = Column(String(255), nullable=False)
    user_answer = Column(String(255), nullable=False)
    quiz_type = Column(String(50), nullable=False)
    folder_id = Column(Integer, nullable=True)  # folder_id도 수정 필요