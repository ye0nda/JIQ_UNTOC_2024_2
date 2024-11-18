from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_folderdb
from quiz.quiz_crud import save_generated_quizzes
from quiz.quiz_schema import QuizResponse
import openai
import os
from io import BytesIO
from PyPDF2 import PdfReader
import json

router = APIRouter()

# OpenAI API Key 설정
openai.api_key = os.getenv("OPENAI_API_KEY", "your-openai-api-key")

@router.post("/upload/", response_model=list[QuizResponse])
async def upload_and_generate_quiz(file: UploadFile = File(...), db: Session = Depends(get_folderdb)):
    # 파일 확장자 확인
    if not (file.filename.endswith(".txt") or file.filename.endswith(".pdf")):
        raise HTTPException(status_code=400, detail="Only .txt and .pdf files are supported.")
    
    # 텍스트 파일 처리
    if file.filename.endswith(".txt"):
        content = await file.read()
        text = content.decode("utf-8")
    # PDF 파일 처리
    elif file.filename.endswith(".pdf"):
        text = extract_text_from_pdf(file)
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type.")

    # OpenAI 프롬프트 생성
    prompt = f"""
    You are a quiz generator. Based on the following text, create 3 quizzes. 
    Each quiz should include:
    - A question
    - A correct answer
    - Four options (including the correct answer)

    Provide the quizzes in the following JSON format:
    [
        {{
            "question": "Your question here",
            "correct_answer": "Correct answer here",
            "options": ["Option1", "Option2", "Option3", "Correct answer"]
        }},
        ...
    ]

    Text:
    {text}
    """
    
    # OpenAI API 호출
    try:
        response = openai.ChatCompletion.create(  # ChatCompletion으로 변경
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
        )
        quizzes = response['choices'][0]['message']['content']
    except openai.error.OpenAIError as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API Error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected Error: {e}")
    
    # GPT 응답 JSON 파싱
    try:
        quizzes_data = json.loads(quizzes)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Failed to parse GPT response.")

    # 데이터베이스에 저장
    saved_quizzes = save_generated_quizzes(db=db, quizzes=quizzes_data)
    return saved_quizzes

# PDF 텍스트 추출 함수
def extract_text_from_pdf(file: UploadFile) -> str:
    try:
        pdf_reader = PdfReader(BytesIO(file.file.read()))  # 파일 내용을 BytesIO로 처리
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text.strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to extract text from PDF: {e}")