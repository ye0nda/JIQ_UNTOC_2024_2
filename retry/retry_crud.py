import openai
from sqlalchemy.orm import Session
import json
from PyPDF2 import PdfReader
import os
from models import Quiz
from datetime import datetime

openai.api_key = os.getenv("OPENAI_API_KEY")

def extract_text_from_file(file_path: str) -> str:
    """
    주어진 파일 경로에서 텍스트를 추출합니다.
    """
    if file_path.endswith(".pdf"):
        reader = PdfReader(file_path)
        return "".join(page.extract_text() for page in reader.pages)
    elif file_path.endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as txt_file:
            return txt_file.read()
    else:
        raise ValueError("Unsupported file format")

def clean_and_parse_gpt_response(content: str):
    """
    GPT 응답에서 JSON 코드 블록을 정리하고 파싱합니다.
    """
    if not content or content.strip() == "":
        raise ValueError("GPT 응답이 비어 있습니다.")

    if content.startswith("```json"):
        content = content[7:]  # "```json" 제거
    elif content.startswith("```"):
        content = content[3:]  # "```" 제거

    if content.endswith("```"):
        content = content[:-3]  # 끝부분 "```" 제거

    content = content.strip()

    try:
        content = bytes(content, "utf-8").decode("unicode_escape")
    except Exception as e:
        raise ValueError(f"UTF-8 디코딩 오류: {str(e)}")

    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON 파싱 오류: {str(e)}")

def process_quiz_generation(file_path: str, db: Session):
    """
    파일에서 텍스트를 추출하고 GPT를 사용하여 퀴즈를 생성한 후 데이터베이스에 저장합니다.
    """
    try:
        # 텍스트 추출
        file_text = extract_text_from_file(file_path)

        # GPT를 사용하여 퀴즈 생성
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You're a problem generator. I'll give you textual material on a subject, "
                        "and you'll create questions based on it. Questions should be in JSON format with fields: "
                        "question number, question, answer, question type, and commentary. Generate one question per 30 characters."
                    )
                },
                {"role": "user", "content": file_text}
            ],
            temperature=0.7,
            max_tokens=2000,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )

        quiz_data = response["choices"][0]["message"]["content"]
        quizzes = clean_and_parse_gpt_response(quiz_data)

        # 데이터베이스에 저장
        for item in quizzes:
            new_quiz = Quiz(
                quiz_number=item.get("quiz_number"),
                quiz_question=item.get("quiz_question"),
                quiz_answer=item.get("quiz_answer"),
                quiz_type=item.get("quiz_type"),
            )
            db.add(new_quiz)
        db.commit()

        return quizzes
    except Exception as e:
        raise Exception(f"Failed to generate quiz: {str(e)}")
