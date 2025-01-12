from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_quizdb
from quiz.quiz_crud import generate_quiz_from_file, extract_text_from_file
import os
from pydantic import BaseModel
from models import Quiz, Retry
from typing import List

router = APIRouter(prefix="/quiz", tags=["quiz"])

class UserAnswer(BaseModel):
    quiz_id: int
    user_answer: str

class SubmitAnswersRequest(BaseModel):
    answers: List[UserAnswer]

# 파일 경로 기반 퀴즈 생성 엔드포인트
@router.post("/generate-from-file")
async def generate_quiz_from_file_path(
    file_path: str, db: Session = Depends(get_quizdb)
):
    """
    프론트엔드에서 제공된 파일 경로를 기반으로 퀴즈를 생성합니다.
    """
    try:
        # 파일 경로 유효성 확인
        if not os.path.exists(file_path):
            raise HTTPException(status_code=400, detail="유효하지 않은 파일 경로입니다.")
        
        # 파일에서 텍스트 추출
        file_text = extract_text_from_file(file_path)
        if not file_text.strip():
            raise HTTPException(status_code=400, detail="파일에서 텍스트를 추출할 수 없습니다.")
        
        # OpenAI를 사용해 퀴즈 생성
        response = generate_quiz_from_file(file_text, db)

        return {"message": "Quiz generated successfully", "result": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/submit")
async def submit_answers(
    request: SubmitAnswersRequest, db: Session = Depends(get_quizdb)
):
    """
    사용자가 제출한 답변을 채점합니다.
    """
    try:
        correct_count = 0
        total_questions = len(request.answers)
        incorrect_questions = []

        for user_answer in request.answers:
            quiz = db.query(Quiz).filter(Quiz.quiz_id == user_answer.quiz_id).first()
            if not quiz:
                raise HTTPException(status_code=404, detail=f"Quiz ID {user_answer.quiz_id} not found")

            # 정답 비교
            if quiz.quiz_answer.strip().lower() == user_answer.user_answer.strip().lower():
                correct_count += 1
                is_correct = True
            else:
                incorrect_questions.append({
                    "quiz_id": quiz.quiz_id,
                    "question": quiz.quiz_question,
                    "correct_answer": quiz.quiz_answer,
                    "user_answer": user_answer.user_answer,
                })
                is_correct = False

            # Retry 테이블에 기록 (선택 사항)
            retry_entry = Retry(
                quiz_id=quiz.quiz_id,
                user_id=1,  # 사용자 ID (로그인 기능이 있다면 연결 필요)
                is_correct=is_correct,
            )
            db.add(retry_entry)

        db.commit()

        return {
            "message": "Answers submitted successfully",
            "total_questions": total_questions,
            "correct_count": correct_count,
            "incorrect_questions": incorrect_questions
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))