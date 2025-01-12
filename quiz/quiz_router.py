from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_quizdb
from quiz.quiz_crud import generate_quiz_from_file
import os

router = APIRouter(prefix="/quiz", tags=["quiz"])

@router.post("/generate-from-file")
async def generate_quiz_from_file_path(
    file_path: str, db: Session = Depends(get_quizdb)
):
    """
    프론트엔드에서 전달된 파일 경로를 기반으로 퀴즈를 생성합니다.
    """
    try:
        # 파일 확인
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")

        # CRUD 함수 호출 (텍스트 추출 및 처리 로직을 CRUD로 이동)
        response = process_quiz_generation(file_path, db)

        return {"message": "Quiz generated successfully", "result": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
