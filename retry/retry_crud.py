from sqlalchemy.orm import Session
from models import Retry

# 오답 기록 저장
def save_retry(db: Session, user_id: int, quiz_id: int, is_correct: bool):
    retry = Retry(
        user_id=user_id,
        quiz_id=quiz_id,
        is_correct=is_correct,
    )
    db.add(retry)
    db.commit()
    db.refresh(retry)
    return retry

# 특정 사용자의 오답 조회
def get_incorrect_retries(db: Session, user_id: int):
    return db.query(Retry).filter_by(user_id=user_id, is_correct=False).all()
