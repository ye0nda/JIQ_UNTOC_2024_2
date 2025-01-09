from sqlalchemy.orm import Session
from models import File

def create_file(db: Session, file_name: str, user_id: int):
    new_file = File(file_name=file_name, user_id=user_id)
    db.add(new_file)
    db.commit()
    db.refresh(new_file)
    return new_file

def get_files_by_user(db: Session, user_id: int):
    return db.query(File).filter(File.user_id == user_id).all()

def delete_file(db: Session, file_id: int, user_id: int):
    file = db.query(File).filter(File.file_id == file_id, File.user_id == user_id).first()
    if file:
        db.delete(file)
        db.commit()
        return {"message": "File deleted successfully"}
    return {"error": "File not found or not authorized"}

import PyPDF2

def extract_text_from_pdf(file_path: str) -> str:
    """PDF 파일에서 텍스트를 추출합니다."""
    text = ""
    with open(file_path, "rb") as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        for page in reader.pages:
            text += page.extract_text()
    return text

def extract_text_from_txt(file_path: str) -> str:
    """텍스트 파일에서 텍스트를 추출합니다."""
    with open(file_path, "r", encoding="utf-8") as txt_file:
        return txt_file.read()