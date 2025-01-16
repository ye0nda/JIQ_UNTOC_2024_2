from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_quizdb
from quiz.quiz_crud import generate_quiz_from_file, extract_text_from_file, split_text_by_limit
from pydantic import BaseModel
from models import Quiz, Retry
from typing import List
from retry.retry_crud import save_retry
import os
import shutil

router = APIRouter(prefix="/quiz", tags=["quiz"])

class UserAnswer(BaseModel):
    quiz_id: int
    user_answer: str

class SubmitAnswersRequest(BaseModel):
    answers: List[UserAnswer]

UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 파일 업로드 기반 퀴즈 생성 엔드포인트
@router.post("/generate-from-file")
async def generate_quiz_from_uploaded_file(
    file: UploadFile = File(...), db: Session = Depends(get_quizdb)
):
    """
    업로드된 파일을 기반으로 퀴즈를 생성합니다.
    """
    try:
        # 업로드된 파일 저장
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # quiz_id 생성 (현재 최대 quiz_id를 가져와 +1)
        max_quiz_id = db.query(func.max(Quiz.quiz_id)).scalar() or 0
        quiz_id = max_quiz_id + 1

        # 텍스트 추출
        file_text = extract_text_from_file(file_path)
        if not file_text.strip():
            raise HTTPException(status_code=400, detail="파일 내용이 비어 있습니다.")

        # 텍스트 분할 및 퀴즈 생성
        text_chunks = split_text_by_limit(file_text)
        all_questions = []

        for chunk in text_chunks:
            response = generate_quiz_from_file(chunk, db, quiz_id=quiz_id)
            if response:
                all_questions.extend(response)

        if not all_questions:
            raise HTTPException(status_code=400, detail="퀴즈를 생성할 수 없습니다.")

        # quiz_id를 문자열로 변환하여 반환
        return {
            "message": "Quiz generated successfully",
            "quiz_id": quiz_id,  # 문자열 변환
            "result": all_questions,
        }
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
    
@router.get("/get-quiz/{quiz_id}")
async def get_quiz(quiz_id: int, db: Session = Depends(get_quizdb)):
    try:
        quizzes = db.query(Quiz).filter(Quiz.quiz_id == quiz_id).order_by(Quiz.quiz_number).all()

        if not quizzes:
            raise HTTPException(status_code=404, detail=f"Quiz ID {quiz_id} not found")

        quiz_list = [
            {
                "quiz_number": quiz.quiz_number,
                "quiz_question": quiz.quiz_question,
            }
            for quiz in quizzes
        ]
        print(f"Quiz List: {quiz_list}")

        return {
            "quiz_id": quiz_id,
            "quizzes": quiz_list,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
