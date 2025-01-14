from sqlalchemy.orm import Session
from sqlalchemy.future import select # 비동기 쿼리용
from datetime import datetime
from models import Retry

def save_retry(db: Session, incorrect_answers: list[dict]):
    """
    오답 데이터를 데이터베이스에 저장합니다.
    :param db: 데이터베이스 세션
    :param quiz_id: 퀴즈 아이디디
    :param incorrect_answers: 오답 리스트 (문제, 사용자 답변, 정답 포함함)
    """
    if attempt_time is None:
        attempt_time = datetime.now()

    for answer in incorrect_answers:
        entry = Retry(
            retry_id=answer["quiz_id"],
            user_answer=answer["user_answer"],
            correct_answer=answer["correct_answer"],
            retry_question=answer["question"],
            attempted_at=attempt_time
        )
        db.add(entry)
    db.commit()
    
    return Retry

async def get_incorrect_answers_by_quiz_id(db: Session, quiz_id: int):
    """
    주어진 퀴즈 아이디에 해당하는 오답 데이터를 비동기적으로 조회합니다.
    :param db: 데이터베이스 세션
    :param quiz_id: 퀴즈 아이디
    :return: 오답 데이터 리스트
    """

    try:
        # 오답 테이블에서 퀴즈 아이디와 일치하는 오답 데이터를 조회
        result = await db.execute(select(Retry).filter(Retry.quiz_id == quiz_id))
        return result.scalars().all() # 비동기적으로 결과 반환
    except Exception as e:
        raise Exception(f"Error retrieving incorrect answers: {str(e)}")
