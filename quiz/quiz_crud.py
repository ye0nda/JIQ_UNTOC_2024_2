import openai
from sqlalchemy.orm import Session
from models import Quiz
from quiz.quiz_schema import QuizCreate
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

# 퀴즈 생성 함수
def create_quiz_from_file(db: Session, file_content: str, quiz_data: QuizCreate):
    if not file_content:
        raise ValueError("파일 내용이 비어 있습니다.")

    # ChatGPT 프롬프트 생성
    prompt = (
        f"다음 내용을 기반으로 {quiz_data.question_count}개의 {quiz_data.type} 퀴즈를 생성하세요.\n"
        "퀴즈는 JSON 형식으로 반환해야 하며, 각 퀴즈는 다음 필드를 포함합니다:\n"
        "- 질문 번호 (number)\n"
        "- 질문 내용 (question)\n"
        "- 정답 (answer)\n"
        "- 질문 유형 (type)\n"
        "- 객관식 보기 (선택 사항, multiple_choice_options)\n\n"
        f"내용: {file_content}"
    )

    # GPT-4 Mini API 호출
    try:
        response = openai.ChatCompletion.create(
            model="chatgpt-4-mini",
            messages=[
                {"role": "system", "content": "You are a quiz generator. Create JSON formatted quizzes based on the input."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000,
            n=1
        )
    except Exception as e:
        raise ValueError(f"OpenAI API 호출 오류: {e}")

    generated_text = response['choices'][0]['message']['content'].strip()

    try:
        quizzes_json = eval(generated_text)  # 응답 JSON을 파싱
    except Exception as e:
        raise ValueError(f"응답 파싱 오류: {e}")

    quizzes = []
    for quiz_json in quizzes_json:
        try:
            quiz = Quiz(
                quiz_number=quiz_json["number"],
                quiz_question=quiz_json["question"],
                quiz_answer=quiz_json["answer"],
                quiz_type=quiz_json["type"],
            )
            db.add(quiz)
            quizzes.append(quiz)
        except KeyError as e:
            print(f"퀴즈 데이터 누락: {e}")
            continue

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise ValueError(f"DB 저장 오류: {e}")

    return quizzes
