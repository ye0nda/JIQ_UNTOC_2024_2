from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_filedb
from quiz.quiz_crud import create_quiz_from_file
from quiz.quiz_schema import QuizCreate, QuizResponse
from file.file_router import upload_file

router = APIRouter(prefix="/quiz", tags=["quiz"])

@router.post("/from-file", response_model=list[QuizResponse])
async def generate_quiz_from_file(
    quiz: QuizCreate,
    file_content: str,  # 업로드된 파일에서 추출된 텍스트를 받아옵니다.
    db: Session = Depends(get_filedb)
):
    try:
        # 파일 내용 기반 퀴즈 생성
        return create_quiz_from_file(db, file_content, quiz)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))