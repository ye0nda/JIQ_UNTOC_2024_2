from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_quizdb
from quiz.quiz_crud import create_quiz_from_file
from quiz.quiz_schema import QuizCreate, QuizResponse
from file.file_router import upload_file

router = APIRouter(prefix="/quiz", tags=["quiz"])

@router.post("/from-file", response_model=list[QuizResponse])
async def generate_quiz_from_file(
    quiz: QuizCreate,
    file_content: str,
    db: Session = Depends(get_quizdb),  # Quiz용 세션 사용
):
    try:
        print("Quiz Data:", quiz)
        print("File Content:", file_content)
        return create_quiz_from_file(db, file_content, quiz)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))