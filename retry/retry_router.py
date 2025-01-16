from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_retrydb
from retry.retry_crud import save_retry, get_incorrect_answers_by_quiz_id
from retry.retry_schema import RetryCreate, Retry
from typing import List

router = APIRouter(prefix="/retry", tags=["retry"])

@router.post("/", response_model=Retry)
async def save_retry_attempt(
    retry_data: RetryCreate,
    db: Session = Depends(get_retrydb)
):
    """
    오답 기록을 저장합니다.
    """
    try:
        saved_retry = save_retry(
            db, retry_data.quiz_id, retry_data.is_correct
        )
        return saved_retry
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"오답 기록 저장 실패: {str(e)}")
    

@router.get("/{quiz_id}")
async def get_incorrect_answers(quiz_id: int, db: Session = Depends(get_retrydb)):
    """
    퀴즈 아이디에 대한 오답 데이터를 조회합니다.
    :param quiz_id: 사용자가 요청한 퀴즈 아이디
    :param db: 오답 데이터베이스 세션
    :return: 오답 리스트
    """

    try:
        # 오답 DB에서 데이터 조회
        incorrect_answers = await get_incorrect_answers_by_quiz_id(db, quiz_id)
        if not incorrect_answers:
            raise HTTPException(status_code=404, defail=f"No incorrect answers found for quiz ID {quiz_id}")
        return {"incorrect_answers": incorrect_answers}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving incorrect answers: {str(e)}")