from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_retrydb
from models import Retry as SQLRetry  # SQLAlchemy 모델 사용

router = APIRouter(prefix="/retry", tags=["retry"])

@router.get("/incorrect-answers/{quiz_id}")
async def get_incorrect_answers(
    quiz_id: int, db: Session = Depends(get_retrydb)
):
    """
    주어진 quiz_id에 대한 오답 데이터를 조회합니다.
    """
    try:
        # SQLAlchemy 모델을 사용하여 오답 데이터 조회 (중복 제거)
        incorrect_answers = db.query(
            SQLRetry.quiz_number,
            SQLRetry.retry_question,
            SQLRetry.correct_answer
        ).filter(
            SQLRetry.quiz_id == quiz_id,
            SQLRetry.is_correct == False  # 오답만 필터링
        ).distinct().all()  # 중복 제거

        if not incorrect_answers:
            raise HTTPException(
                status_code=404, 
                detail=f"No incorrect answers found for Quiz ID {quiz_id}"
            )

        # 반환 데이터 구성
        results = [
            {
                "quiz_number": answer.quiz_number,
                "retry_question": answer.retry_question,
                "correct_answer": answer.correct_answer
            }
            for answer in incorrect_answers
        ]

        return {
            "quiz_id": quiz_id,
            "incorrect_answers": results
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving incorrect answers: {str(e)}"
        )
