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

def generate_quiz_from_file(file_text: str, user_id: int, db: Session):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You're a problem generator. I'll give you textual material on a subject, "
                        "and you'll create questions based on it. Questions should be in JSON format with fields: "
                        "question number, question, answer, and question type."
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

        # OpenAI 응답 출력 (디버깅용)
        print("OpenAI Response:", response)

        # 응답 데이터 파싱
        quiz_data = response["choices"][0]["message"]["content"]
        quizzes = parse_quiz_response(quiz_data)

        # 중복 제거 후 저장
        unique_quizzes = {item["question"]: item for item in quizzes}.values()
        for item in unique_quizzes:
            if item["question"] and item["answer"]:  # 유효성 검사
                new_quiz = Quiz(
                    quiz_number=item["question_number"],
                    quiz_question=item["question"],
                    quiz_answer=item["answer"],
                    quiz_type=item["question_type"],
                    user_id=user_id,
                )
                db.add(new_quiz)
        db.commit()

        return {"message": "Quizzes generated successfully"}
    except Exception as e:
        raise Exception(f"Failed to generate quiz: {str(e)}")
