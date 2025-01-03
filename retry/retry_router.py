from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_retrydb
from retry.retry_crud import save_retry, get_incorrect_retries
from retry.retry_schema import RetryCreate, Retry

router = APIRouter(prefix="/retry", tags=["retry"])

@router.post("/", response_model=Retry)
async def save_retry_attempt(retry_data: RetryCreate, db: Session = Depends(get_retrydb)):
    try:
        return save_retry(
            db, retry_data.user_id, retry_data.quiz_id, retry_data.is_correct
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=list[Retry])
async def get_user_incorrect_retries(user_id: int, db: Session = Depends(get_retrydb)):
    return get_incorrect_retries(db, user_id)
