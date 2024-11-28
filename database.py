from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv
import os

# .env 파일 로드
load_dotenv()

# 환경 변수에서 데이터베이스 URL 가져오기
FOLDER_DATABASE_URL = os.getenv("FOLDER_DATABASE_URL", "mysql+pymysql://root:1029@localhost:3306/folder")
FILE_DATABASE_URL = os.getenv("FILE_DATABASE_URL", "mysql+pymysql://root:1029@localhost:3306/file")
QUIZ_DATABASE_URL = os.getenv("FILE_DATABASE_URL", "mysql+pymysql://root:1029@localhost:3306/quiz")

# 엔진 생성
folder_engine = create_engine(FOLDER_DATABASE_URL, echo=False)
file_engine = create_engine(FILE_DATABASE_URL, echo=False)
quiz_engine = create_engine(QUIZ_DATABASE_URL, echo=False)

# 세션 로컬 생성
FolderSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=folder_engine)
FileSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=file_engine)
QuizSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=quiz_engine)

# 베이스 클래스 정의
class FolderBase(DeclarativeBase):
    pass


class FileBase(DeclarativeBase):
    pass

class QuizBase(DeclarativeBase):
    pass

# 세션 의존성 함수 정의=
def get_folderdb():
    db = FolderSessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_filedb():
    db = FileSessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_quizdb():
    db = FileSessionLocal()
    try:
        yield db
    finally:
        db.close()

# 데이터베이스 초기화
def init_databases():
    from models import Folder, File
    FolderBase.metadata.create_all(bind=folder_engine)
    FileBase.metadata.create_all(bind=file_engine)
    QuizBase.metadata.create_all(bind=quiz_engine)