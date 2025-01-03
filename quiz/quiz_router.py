from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_quizdb
from quiz.quiz_crud import generate_quiz_from_file
import os

router = APIRouter(prefix="/quiz", tags=["quiz"])

@router.post("/generate-from-file")
async def generate_quiz_from_file_path(
    file_path: str, user_id: int, db: Session = Depends(get_quizdb)
):
    """
    업로드된 파일 경로를 기반으로 퀴즈를 생성합니다.
    """
    try:
        # 파일 확인
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")

        # 텍스트 추출
        if file_path.endswith(".pdf"):
            from PyPDF2 import PdfReader
            reader = PdfReader(file_path)
            text = "".join(page.extract_text() for page in reader.pages)
        elif file_path.endswith(".txt"):
            with open(file_path, "r", encoding="utf-8") as txt_file:
                text = txt_file.read()
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")

        # GPT를 사용하여 퀴즈 생성
        quiz_generation_result = generate_quiz_from_file(text, user_id, db)

        return {"message": "Quiz generated successfully", "result": quiz_generation_result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
