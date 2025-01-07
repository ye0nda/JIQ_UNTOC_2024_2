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
                quiz_number=item["question_number"],
                quiz_question=item["question"],
                quiz_answer=item["answer"],
                quiz_type=item["question_type"],
                user_id=user_id,
                created_at=datetime.utcnow(),
            )
            db.add(new_quiz)
        db.commit()

        return {"message": "Quizzes generated successfully"}
    except Exception as e:
        raise Exception(f"Failed to generate quiz: {str(e)}")

import json

def parse_quiz_response(quiz_data: str):
    """
    JSON 형식의 퀴즈 데이터를 리스트로 변환합니다.
    
    Args:
        quiz_data (str): JSON 형식의 문자열 데이터.
    
    Returns:
        list[dict]: 퀴즈 목록.
    
    Raises:
        ValueError: JSON 데이터가 유효하지 않을 때.
    """
    try:
        # JSON 데이터 파싱
        parsed_data = json.loads(quiz_data)
        
        # 리스트 형식인지 확인
        if not isinstance(parsed_data, list):
            raise ValueError("JSON 데이터는 리스트 형식이어야 합니다.")

        # 필수 필드 확인
        for item in parsed_data:
            if not all(key in item for key in ["question_number", "question", "answer", "question_type"]):
                raise ValueError(f"퀴즈 데이터에 필요한 필드가 누락되었습니다: {item}")

        return parsed_data  # 파싱된 리스트 반환

    except json.JSONDecodeError as e:
        raise ValueError(f"JSON 파싱 오류: {str(e)}")
    except Exception as e:
        raise ValueError(f"예기치 않은 오류 발생: {str(e)}")
