import openai
from sqlalchemy.orm import Session
from models import Quiz
from quiz.quiz_schema import QuizCreate
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

import openai
from sqlalchemy.orm import Session
from models import Quiz
from datetime import datetime
import json

openai.api_key = "your_openai_api_key"

def generate_quiz_from_file(file_text: str, user_id: int, db: Session):
    """GPT를 사용하여 파일 텍스트에서 퀴즈를 생성합니다."""
    try:
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
        quizzes = parse_quiz_response(quiz_data)

        for item in quizzes:
            new_quiz = Quiz(
                quiz_number=item["question number"],
                quiz_question=item["question"],
                quiz_answer=item["answer"],
                quiz_type=item["question type"],
                user_id=user_id,
                created_at=datetime.utcnow(),
            )
            db.add(new_quiz)
        db.commit()

        return {"message": "Quizzes generated successfully"}
    except Exception as e:
        raise Exception(f"Failed to generate quiz: {str(e)}")

def parse_quiz_response(quiz_data: str):
    """JSON 형태의 퀴즈 데이터를 파싱"""
    try:
        return json.loads(quiz_data)
    except json.JSONDecodeError as e:
        raise Exception(f"Failed to parse quiz data: {str(e)}")
