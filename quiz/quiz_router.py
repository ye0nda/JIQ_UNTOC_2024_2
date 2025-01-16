from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from database import get_quizdb
from quiz.quiz_crud import generate_quiz_from_file, extract_text_from_file
from pydantic import BaseModel
from models import Quiz, Retry
from typing import List
from retry.retry_crud import save_retry
import os

router = APIRouter(prefix="/quiz", tags=["quiz"])

class UserAnswer(BaseModel):
    quiz_id: int
    user_answer: str

class SubmitAnswersRequest(BaseModel):
    answers: List[UserAnswer]

# 파일 업로드 기반 퀴즈 생성 엔드포인트
@router.post("/generate-from-file")
async def generate_quiz_from_uploaded_file(
    file: UploadFile = File(...), db: Session = Depends(get_quizdb)
):
    """
    업로드된 파일을 기반으로 퀴즈를 생성합니다.
    """
    try:
        # 업로드된 파일 읽기
        file_content = await file.read()
        if not file_content.strip():
            raise HTTPException(status_code=400, detail="파일 내용이 비어 있습니다.")

        # 텍스트 추출
        file_text = file_content.decode("utf-8")
        
        # OpenAI를 사용해 퀴즈 생성
        response = generate_quiz_from_file(file_text, db)

        return {"message": "Quiz generated successfully", "result": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/user-answers")
async def get_user_answers(request: SubmitAnswersRequest, db: Session = Depends(get_quizdb)):
    """
    사용자가 제출한 답변을 데이터베이스에 저장합니다.
    """
    try:
        for user_answer in request.answers:
            # 답변 저장
            user_answer_entry = Quiz(
                quiz_id=user_answer.quiz_id,
                user_answer=user_answer.user_answer
            )
            db.add(user_answer_entry)

        db.commit()

        return {"message": "Answers saved successfully"}
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

            # Retry 테이블에 저장
            save_retry(db, incorrect_answers=incorrect_questions)

        return {
            "message": "Answers submitted successfully",
            "total_questions": total_questions,
            "correct_count": correct_count,
            "incorrect_questions": incorrect_questions
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
