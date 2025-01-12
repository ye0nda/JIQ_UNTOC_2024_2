import openai
from sqlalchemy.orm import Session
import json
from PyPDF2 import PdfReader
import os
from models import Quiz
from datetime import datetime

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
        content = bytes(content, "utf-8").decode("unicode_escape")  # 유니코드 이스케이프 처리
    except Exception as e:
        raise ValueError(f"UTF-8 디코딩 오류: {str(e)}")

    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON 파싱 오류: {str(e)}")


def generate_quiz_from_file(file_text: str, db: Session, max_questions: int = 10):
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

        print("Normalized Quizzes:", quizzes)  # 디버깅용 출력

        if not isinstance(quizzes, list):
            raise ValueError("응답 데이터가 JSON 배열 형식이 아닙니다.")

        quizzes = quizzes[:max_questions]

        for item in quizzes:
            question_number = item.get("question_number")
            question = item.get("question")
            answer = item.get("answer")

            if not question_number or not question or not answer:
                raise ValueError(f"JSON 데이터에 누락된 필드가 있습니다: {item}")

            if not isinstance(answer, str):
                raise ValueError(f"Answer가 문자열이 아닙니다: {item}")

            # Quiz 객체 생성 및 DB 저장
            new_quiz = Quiz(
                quiz_number=question_number,
                quiz_question=question,
                quiz_answer=answer,
                quiz_type="short_answer",
            )
            db.add(new_quiz)

        db.commit()

        return {"message": "단답형 퀴즈가 성공적으로 생성되었습니다", "questions_created": len(quizzes)}

    except json.JSONDecodeError as e:
        raise ValueError(f"JSON 파싱 오류: {str(e)}")
    except Exception as e:
        db.rollback()
        raise Exception(f"퀴즈 생성 실패: {str(e)}")


def extract_text_from_file(file_path: str) -> str:
    """
    주어진 파일 경로에서 텍스트를 추출합니다.
    현재 PDF와 TXT 파일만 지원합니다.
    """
    if file_path.endswith(".pdf"):
        reader = PdfReader(file_path)
        extracted_text = "".join(page.extract_text() for page in reader.pages)
        # UTF-8로 인코딩 변환
        return extracted_text.encode("utf-8", "ignore").decode("utf-8", "ignore")
    elif file_path.endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as txt_file:
            return txt_file.read()
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