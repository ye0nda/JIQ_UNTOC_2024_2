from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_quizdb
from quiz.quiz_crud import save_generated_quizzes
from quiz.quiz_schema import QuizResponse
import openai
import os
import json
from io import BytesIO
from PyPDF2 import PdfReader

router = APIRouter()

openai.api_key = os.getenv("OPENAI_API_KEY")

@router.post("/upload/", response_model=list[QuizResponse])
async def upload_and_generate_quiz(file: UploadFile = File(...), db: Session = Depends(get_quizdb)):
    if not (file.filename.endswith(".txt") or file.filename.endswith(".pdf")):
        raise HTTPException(status_code=400, detail="Only .txt and .pdf files are supported.")

    if file.filename.endswith(".txt"):
        content = await file.read()
        text = content.decode("utf-8")
    elif file.filename.endswith(".pdf"):
        text = await extract_text_from_pdf(file)

    prompt = f"""You are a quiz generator. Based on the following text, create 3 quizzes..."""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000,
        )
        quizzes = response['choices'][0]['message']['content']
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API Error: {e}")

    try:
        quizzes_data = json.loads(quizzes)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Failed to parse GPT response.")

    saved_quizzes = save_generated_quizzes(db=db, quizzes=quizzes_data)
    return saved_quizzes

async def extract_text_from_pdf(file: UploadFile) -> str:
    file_data = await file.read()
    pdf_reader = PdfReader(BytesIO(file_data))
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text.strip()