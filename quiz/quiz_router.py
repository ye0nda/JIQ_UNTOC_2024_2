from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_quizdb, get_retrydb
from quiz.quiz_crud import generate_quiz_from_file, extract_text_from_file, split_text_by_limit, update_user_answer
from pydantic import BaseModel
from models import Quiz, Retry
from typing import List
from retry.retry_crud import save_retry
import os
import shutil

router = APIRouter(prefix="/quiz", tags=["quiz"])

class UserAnswer(BaseModel):
    quiz_id: int
    quiz_number: int
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
async def submit_user_answers(
    request: SubmitAnswersRequest, db: Session = Depends(get_quizdb)
):
    """
    여러 답변을 한 번에 업데이트하고, 채점 후 retry_attempts 테이블에 결과를 저장.
    """
    try:
        retry_entries = []

        for answer in request.answers:
            # quiz_id와 quiz_number로 Quiz 항목 찾기
            quiz_entry = db.query(Quiz).filter(
                Quiz.quiz_id == answer.quiz_id,
                Quiz.quiz_number == answer.quiz_number
            ).first()

            if not quiz_entry:
                print(f"Quiz not found for quiz_id={answer.quiz_id} and quiz_number={answer.quiz_number}")
                continue

            # user_answer 업데이트
            quiz_entry.user_answer = answer.user_answer
            db.add(quiz_entry)

            # 채점 로직
            is_correct = quiz_entry.quiz_answer.strip().lower() == answer.user_answer.strip().lower()

            # retry_attempts 테이블에 저장할 데이터 준비
            retry_entries.append(
                Retry(
                    quiz_id=answer.quiz_id,
                    quiz_number=answer.quiz_number,
                    retry_question=quiz_entry.quiz_question,
                    user_answer=answer.user_answer,
                    correct_answer=quiz_entry.quiz_answer,
                    is_correct=is_correct
                )
            )

        # 모든 변경 사항 커밋
        db.commit()

        # retry_attempts 테이블에 데이터 저장
        db.add_all(retry_entries)
        db.commit()

        return {"message": "User answers updated and results saved successfully"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating user answers: {str(e)}")

    
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

@router.get("/results/{quiz_id}")
async def get_quiz_results(quiz_id: int, db: Session = Depends(get_retrydb)):
    """
    주어진 퀴즈 ID에 대한 각 문제의 정답 여부만 반환합니다.
    """
    try:
        # Retry 테이블에서 해당 quiz_id에 대한 데이터 조회
        retries = db.query(Retry).filter(Retry.quiz_id == quiz_id).order_by(Retry.quiz_number).all()

        if not retries:
            raise HTTPException(status_code=404, detail=f"No retry data found for Quiz ID {quiz_id}")

        # 결과 생성
        results = []
        for retry in retries:
            results.append({
                "quiz_number": retry.quiz_number,
                "is_correct": retry.is_correct
            })

        return {
            "quiz_id": quiz_id,
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving quiz results: {str(e)}")

