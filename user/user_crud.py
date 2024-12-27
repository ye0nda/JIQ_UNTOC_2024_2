from sqlalchemy.orm import Session
from models import User
from user.user_schema import UserCreate
from passlib.context import CryptContext
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

# 비밀번호 해싱을 위한 설정
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, user: UserCreate):
    try:
        hashed_password = pwd_context.hash(user.password)
        db_user = User(
            username=user.username,
            hashed_password=hashed_password,
            email=user.email
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Username or email already exists.")