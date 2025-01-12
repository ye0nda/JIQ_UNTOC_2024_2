from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_retrydb
from retry.retry_crud import save_retry, get_incorrect_retries
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