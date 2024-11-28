import openai
from sqlalchemy.orm import Session
from models import Quiz
from quiz.quiz_schema import QuizCreate


openai.api_key = "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"

def create_quiz_from_file(db: Session, content: str, quiz_data: QuizCreate):
    # ChatGPT 프롬프트 생성
    prompt = f"Based on the following content, create {quiz_data.question_count} {quiz_data.type} questions with answers:\n\n{content}"
    
    # GPT-4 Turbo API 호출
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",  # GPT-4 Turbo 모델 지정
        messages=[
            {"role": "system", "content": "You are a helpful assistant that generates quizzes."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=2000,  # 응답 길이
        temperature=1   # 출력 다양성 조정
    )

    # 응답에서 질문과 답변 파싱
    generated_text = response['choices'][0]['message']['content'].strip()
    questions_and_answers = generated_text.split("\n")
    
    quizzes = []
    for i, qa in enumerate(questions_and_answers, start=1):
        if "Answer:" in qa:
            question, answer = qa.split("Answer:")
            quiz = Quiz(
                number=i,
                question=question.strip(),
                answer=answer.strip(),
                type=quiz_data.type
            )
            db.add(quiz)
            quizzes.append(quiz)
    
    db.commit()
    return quizzes