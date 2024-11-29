import openai
from sqlalchemy.orm import Session
from models import Quiz
from quiz.quiz_schema import QuizCreate
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

# 파일에서 내용을 읽어오는 함수
def read_file(file_path: str) -> str:
    """파일을 읽어서 텍스트 내용을 반환하는 함수"""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
        return content
    except Exception as e:
        print(f"Error reading file: {e}")
        return ""

# 퀴즈 생성 함수
def create_quiz_from_file(db: Session, file_path: str, quiz_data: QuizCreate):
    # 파일에서 내용을 읽어옵니다
    content = read_file(file_path)
    
    if not content:
        print("파일 내용이 없습니다.")
        return []
    
    # ChatGPT 프롬프트 생성
    prompt = f"Based on the following content, create {quiz_data.question_count} {quiz_data.type} questions with answers:\n\n{content}"
    
    # GPT-4 Turbo API 호출
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",  # 모델 이름 수정
            messages=[
                {
                    "role": "system",
                    "content": "You're a problem generator. I'll give you some textual material on a subject, and you'll create questions based on it. The format of the questions can be a mix of multiple choice, essay, narrative, etc. You answer the questions in JSON format, with the fields: subject, question number, question, answer, question type, multiple choice options (if the question type is not multiple choice, just leave it blank), and commentary. Please include this in your answer. Send me the questions and answer explanations in Korean. The amount of questions should be about one question per 30 characters, so that there is a good variety. Aim for 60% multiple choice, 30% essay, and 10% narrative, based on the content suitability."
                },
                {
                    "role": "user",
                    "content": content,
                }
            ],
            temperature=1,
            max_tokens=2000,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
    except Exception as e:
        print(f"OpenAI API 호출 오류: {e}")
        return []
    
    # 응답에서 질문과 답변 파싱
    generated_text = response['choices'][0]['message']['content'].strip()
    print(generated_text)  # 디버깅용 출력
    
    questions_and_answers = generated_text.split("\n")
    
    quizzes = []
    for i, qa in enumerate(questions_and_answers, start=1):
        if "Answer:" in qa:
            try:
                question, answer = qa.split("Answer:")
                quiz = Quiz(
                    quiz_number=i,  # 'quiz_number'로 수정 (Quiz 모델에 맞게)
                    quiz_question=question.strip(),  # 'quiz_question'으로 수정
                    quiz_answer=answer.strip(),  # 'quiz_answer'으로 수정
                    quiz_type=quiz_data.type  # 타입을 QuizCreate에서 가져온 값으로 설정
                )
                db.add(quiz)
                quizzes.append(quiz)
            except Exception as e:
                print(f"질문 처리 오류: {e}")
                continue
    
    try:
        db.commit()
    except Exception as e:
        db.rollback()  # 에러 발생 시 롤백
        print(f"DB 커밋 오류: {e}")
    
    return quizzes