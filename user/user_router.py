from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt, JWTError
from database import get_userdb
from user.user_crud import create_user, get_user_by_username
from user.user_schema import UserCreate, UserLogin, UserResponse
import os

# 환경 변수에서 JWT 설정
SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(prefix="/user", tags=["user"])

@router.post("/register", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_userdb)):
    try:
        existing_user = get_user_by_username(db, user.username)
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already exists")
        new_user = create_user(db=db, user=user)
        return new_user
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error occurred during registration: {e}")

@router.post("/login")
def login_user(user: UserLogin, db: Session = Depends(get_userdb)):
    try:
        db_user = get_user_by_username(db, user.username)
        if not db_user or not pwd_context.verify(user.password, db_user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        token_data = {"sub": db_user.username}
        token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
        return {"access_token": token, "token_type": "bearer"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error occurred during login: {e}")
