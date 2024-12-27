from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from .file_crud import create_file, delete_file
from .file_schema import FileCreate, FileResponse, FileUploadResponse
from database import get_filedb
from quiz.quiz_crud import create_quiz_from_file
from quiz.quiz_schema import QuizCreate
import os
from PyPDF2 import PdfReader

router = APIRouter()

@router.post("/create-file", response_model=FileResponse)
def upload_file(file: FileCreate, db: Session = Depends(get_filedb)):
    return create_file(db=db, file=file)

@router.delete("/delete-file/{file_id}")
async def delete_folder_endpoint(file_id: int, db: Session = Depends(get_filedb)):
    return delete_file(db=db, file_id=file_id)

@router.post("/upload", response_model=FileUploadResponse)
async def upload_and_generate_quiz(file: UploadFile = File(...), quiz_data: QuizCreate = Depends(), db: Session = Depends(get_filedb)):
    try:
        UPLOAD_DIR = "uploads"

        # 디렉토리 생성
        if not os.path.exists(UPLOAD_DIR):
            os.makedirs(UPLOAD_DIR)

        # 파일 저장 경로
        file_location = os.path.join(UPLOAD_DIR, file.filename)

        # 파일 저장
        with open(file_location, "wb") as f:
            f.write(await file.read())

        # PDF 텍스트 추출
        if file.filename.endswith(".pdf"):
            reader = PdfReader(file_location)
            content = "\n".join(page.extract_text() for page in reader.pages)
        elif file.filename.endswith(".txt"):
            with open(file_location, "r", encoding="utf-8") as f:
                content = f.read()
        else:
            raise HTTPException(status_code=400, detail="지원하지 않는 파일 형식입니다. txt 또는 pdf 파일만 허용됩니다.")

        # 퀴즈 생성 호출
        quizzes = create_quiz_from_file(db=db, file_content=content, quiz_data=quiz_data)

        return {"filename": file.filename, "message": "퀴즈 생성 및 파일 업로드 성공", "quizzes": quizzes}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"파일 처리 중 오류가 발생했습니다: {str(e)}")
