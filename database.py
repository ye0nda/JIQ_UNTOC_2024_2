from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv
import os

# .env 파일 로드
load_dotenv()

# 환경 변수에서 데이터베이스 URL 가져오기
FOLDER_DATABASE_URL = os.getenv("FOLDER_DATABASE_URL", "mysql+pymysql://root:password@localhost:3306/folder")
QUIZ_DATABASE_URL = os.getenv("QUIZ_DATABASE_URL", "mysql+pymysql://root:password@localhost:3306/quiz")
RETRY_DATABASE_URL = os.getenv("RETRY_DATABASE_URL", "mysql+pymysql://root:password@localhost:3306/retry")

# 엔진 생성
# folder_engine = create_engine(FOLDER_DATABASE_URL, echo=False)
folder_engine = create_engine(FOLDER_DATABASE_URL, echo=False)
quiz_engine = create_engine(QUIZ_DATABASE_URL, echo=False)
retry_engine = create_engine(RETRY_DATABASE_URL, echo=False)

# 세션 로컬 생성
FolderSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=folder_engine)
QuizSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=quiz_engine)
RetrySessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=retry_engine)

# 베이스 클래스 정의
class FolderBase(DeclarativeBase):
    pass

class QuizBase(DeclarativeBase):
    pass

class RetryBase(DeclarativeBase):
    pass

# 세션 의존성 함수 정의
def get_folderdb():
    db = FolderSessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_quizdb():
    db = QuizSessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_retrydb():
    db = RetrySessionLocal()
    try:
        yield db
    finally:
        db.close()

# 데이터베이스 초기화 함수
def init_databases():
    from models import Folder, Quiz, Retry
    FolderBase.metadata.create_all(bind=folder_engine)
    QuizBase.metadata.create_all(bind=quiz_engine)
    RetryBase.metadata.create_all(bind=retry_engine)