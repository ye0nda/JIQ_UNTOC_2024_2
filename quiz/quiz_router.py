from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_quizdb
from quiz.quiz_crud import create_quiz_from_file
from quiz.quiz_schema import QuizCreate, QuizResponse
from models import Quiz

router = APIRouter()

@router.post("/from-file", response_model=list[QuizResponse])
async def generate_quiz_from_file(
    quiz: QuizCreate,
    file_content: str,
    db: Session = Depends(get_quizdb),
):
    try:
        print("Quiz Data:", quiz)
        print("File Content:", file_content)
        return create_quiz_from_file(db, file_content, quiz)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/quizzes", response_model=list[QuizResponse])
async def get_all_quizzes(db: Session = Depends(get_quizdb)):
    try:
        quizzes = db.query(Quiz).all()
        return quizzes
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"퀴즈 조회 중 오류가 발생했습니다: {str(e)}")
