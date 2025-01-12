from sqlalchemy.orm import Session
from models import Retry

def save_retry(db: Session, quiz_id: int, is_correct: bool):
    retry = Retry(
        quiz_id=quiz_id,
        is_correct=is_correct,
    )
    db.add(retry)
    db.commit()
    db.refresh(retry)
    return retry

def get_incorrect_retries(db: Session, user_id: int):
    """
    특정 사용자의 오답 기록을 조회합니다.
    """
    return db.query(Retry).filter_by(user_id=user_id, is_correct=False).all()
