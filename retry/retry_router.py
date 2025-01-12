from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_retrydb
from retry.retry_crud import save_retry, get_incorrect_retries
from retry.retry_schema import RetryCreate, Retry
from user.user_router import get_current_user  # 사용자 인증
from typing import List

router = APIRouter(prefix="/retry", tags=["retry"])

@router.post("/", response_model=Retry)
async def save_retry_attempt(
    retry_data: RetryCreate,
    db: Session = Depends(get_retrydb),
    current_user: dict = Depends(get_current_user)
):
    """
    오답 기록을 저장합니다.
    """
    try:
        saved_retry = save_retry(
            db, current_user["id"], retry_data.quiz_id, retry_data.is_correct
        )
        return saved_retry
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"오답 기록 저장 실패: {str(e)}")

@router.get("/", response_model=List[Retry])
async def get_user_incorrect_retries(
    db: Session = Depends(get_retrydb),
    current_user: dict = Depends(get_current_user)
):
    """
    현재 사용자의 오답 기록을 조회합니다.
    """
    try:
        retries = get_incorrect_retries(db, current_user["id"])
        return retries
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"오답 기록 조회 실패: {str(e)}")