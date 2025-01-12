from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_quizdb
from quiz.quiz_crud import generate_quiz_from_file, extract_text_from_file
import os

router = APIRouter(prefix="/quiz", tags=["quiz"])

# 파일 경로 기반 퀴즈 생성 엔드포인트
@router.post("/generate-from-file")
async def generate_quiz_from_file_path(
    file_path: str, db: Session = Depends(get_quizdb)
):
    """
    프론트엔드에서 제공된 파일 경로를 기반으로 퀴즈를 생성합니다.
    """
    try:
        # 파일 경로 유효성 확인
        if not os.path.exists(file_path):
            raise HTTPException(status_code=400, detail="유효하지 않은 파일 경로입니다.")
        
        # 파일에서 텍스트 추출
        file_text = extract_text_from_file(file_path)
        if not file_text.strip():
            raise HTTPException(status_code=400, detail="파일에서 텍스트를 추출할 수 없습니다.")
        
        # OpenAI를 사용해 퀴즈 생성
        response = generate_quiz_from_file(file_text, db)

        return {"message": "Quiz generated successfully", "result": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
