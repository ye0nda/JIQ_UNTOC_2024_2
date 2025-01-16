import openai
from sqlalchemy.orm import Session
import json
from PyPDF2 import PdfReader
import os
from models import Quiz, Retry
from datetime import datetime
from typing import List
import uuid

openai.api_key = os.getenv("OPENAI_API_KEY")

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
        return json.loads(content)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON 파싱 오류: {str(e)}")

def generate_quiz_from_file(file_text: str, db: Session, quiz_id: int, max_questions: int = 10):
    """
    주어진 텍스트 파일 내용으로부터 단답형 퀴즈를 생성합니다. 문제 수를 제한합니다.

    :param file_text: 파일의 내용.
    :param db: 데이터베이스 세션.
    :param max_questions: 생성할 최대 문제 수.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"당신은 문제 생성기입니다. 제가 특정 주제에 대한 텍스트 자료를 제공하면, "
                        f"이를 기반으로 최대 {max_questions}개의 단답형(short_answer) 문제를 생성해주세요. "
                        f"답변은 항상 하나의 단어로만 구성되어야 합니다. "
                        f"문제는 JSON 형식으로 구성되며, 필드는 다음과 같습니다: question number, question, answer."
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

        quiz_data = response["choices"][0]["message"]["content"].strip()
        print("OpenAI Response (Raw):", quiz_data)

        # JSON 데이터 파싱
        quizzes = clean_and_parse_gpt_response(quiz_data)

        # JSON 키를 Python 스타일로 변환
        quizzes = normalize_keys(quizzes)

        if not isinstance(quizzes, list):
            raise ValueError("응답 데이터가 JSON 배열 형식이 아닙니다.")

        # 기존 quiz_number 확인 및 초기화
        existing_numbers = db.query(Quiz.quiz_number).filter(Quiz.quiz_id == quiz_id).all()
        existing_numbers = {num[0] for num in existing_numbers}
        current_number = 1

        total_questions = db.query(Quiz).filter(Quiz.quiz_id == quiz_id).count()

        for idx, item in enumerate(quizzes[:max_questions], start=1):
            if total_questions >= max_questions:
                break

            # 중복되지 않는 quiz_number 생성
            while current_number in existing_numbers:
                current_number += 1

            question_number = current_number
            question = item.get("question")
            answer = item.get("answer")

            if not question or not answer:
                raise ValueError(f"JSON 데이터에 누락된 필드가 있습니다: {item}")

            # Quiz 객체 생성 및 DB 저장
            new_quiz = Quiz(
                quiz_id=quiz_id,
                quiz_number=question_number,
                quiz_question=question,
                quiz_answer=answer,
                quiz_type="short_answer",
            )
            print(f"Attempting to save quiz {question_number}: {question}")
            db.add(new_quiz)
            db.commit()
            print(f"Quiz saved: {new_quiz}")
            existing_numbers.add(current_number)  # 추가된 번호를 기록
            total_questions += 1

        db.commit()
        return {"message": f"Quiz {quiz_id} created successfully", "quiz_id": quiz_id}

    except Exception as e:
        db.rollback()
        raise Exception(f"퀴즈 생성 실패: {str(e)}")

def extract_text_from_file(file_path: str) -> str:
    """
    주어진 파일 경로에서 텍스트를 추출합니다.
    현재 PDF와 TXT 파일만 지원합니다.
    """
    if file_path.endswith(".pdf"):
        try:
            reader = PdfReader(file_path)
            extracted_text = ""
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    extracted_text += text
            # UTF-8로 안전하게 변환
            return extracted_text.encode("utf-8", "ignore").decode("utf-8", "ignore")
        except Exception as e:
            raise ValueError(f"PDF 텍스트 추출 실패: {str(e)}")
    elif file_path.endswith(".txt"):
        try:
            with open(file_path, "r", encoding="utf-8") as txt_file:
                return txt_file.read()
        except Exception as e:
            raise ValueError(f"TXT 파일 읽기 실패: {str(e)}")
    else:
        raise ValueError("지원되지 않는 파일 형식입니다.")

def normalize_keys(data):
    """
    JSON 데이터의 키를 Python 스타일로 변환.
    예: 'question number' -> 'question_number'
    """
    if isinstance(data, list):
        return [normalize_keys(item) for item in data]
    elif isinstance(data, dict):
        return {key.replace(" ", "_"): value for key, value in data.items()}
    return data

def update_user_answer(db: Session, quiz_id: int, quiz_number: int, user_answer: str):
    # 해당 quiz_id와 quiz_number를 가진 퀴즈를 조회
    quiz_entry = db.query(Quiz).filter(
        Quiz.id == quiz_id,
        Quiz.number == quiz_number
    ).first()
    
    if not quiz_entry:
        raise ValueError("해당 퀴즈 항목을 찾을 수 없습니다.")
    
    # user_answer 업데이트
    quiz_entry.user_answer = user_answer
    db.commit()
    db.refresh(quiz_entry)
    return quiz_entry


def split_text_by_limit(text: str, max_length: int = 8000) -> List[str]:
    """
    텍스트를 최대 길이에 맞게 분할합니다.
    """
    paragraphs = text.split("\n")
    chunks = []
    current_chunk = ""

    for paragraph in paragraphs:
        if len(current_chunk) + len(paragraph) + 1 <= max_length:
            current_chunk += paragraph + "\n"
        else:
            chunks.append(current_chunk.strip())
            current_chunk = paragraph + "\n"

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks

def save_retry(db: Session, incorrect_answers: List[dict]):
    """
    오답 데이터를 retry_attempts 테이블에 저장합니다.
    """
    for answer in incorrect_answers:
        entry = Retry(
            quiz_id=answer["quiz_id"],
            quiz_number=answer["quiz_number"],
            user_answer=answer["user_answer"],
            correct_answer=answer["correct_answer"],
            retry_question=answer["retry_question"],
            is_correct=answer["is_correct"],
        )
        db.add(entry)
    db.commit()