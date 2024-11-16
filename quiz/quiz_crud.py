from sqlalchemy.orm import Session
from quiz.quiz_schema import QuizCreate
from typing import List

def save_generated_quizzes(db: Session, quizzes: List[dict]):
    from models import Quiz
    saved_quizzes = []
    for quiz in quizzes:
        db_quiz = Quiz(
            question=quiz["question"],
            answer=quiz["answer"],
            options=quiz["options"],
            category=quiz.get("category", None)
        )
        db.add(db_quiz)
        db.commit()
        db.refresh(db_quiz)
        saved_quizzes.append(db_quiz)
    return saved_quizzes