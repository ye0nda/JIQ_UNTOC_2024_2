from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_quizdb
from quiz.quiz_crud import generate_quiz_from_file
from user.user_router import get_current_user
import os

router = APIRouter(prefix="/quiz", tags=["quiz"])

@router.post("/generate-from-file")
async def generate_quiz_from_file_path(
    file_path: str, db: Session = Depends(get_quizdb), current_user = Depends(get_current_user)
):
    """
    업로드된 파일 경로를 기반으로 퀴즈를 생성합니다.
    """
    try:
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")

        # 파일 확인 및 텍스트 추출 로직 (생략)
        
        quiz_generation_result = generate_quiz_from_file("dummy_text", current_user.id, db)
        return {"message": "Quiz generated successfully", "result": quiz_generation_result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
