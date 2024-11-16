from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
FOLDER_DB_NAME = os.getenv("FOLDER_DB_NAME", "folder_db")
DB_PORT = os.getenv("DB_PORT", 3306)

SQLALCHEMY_DATABASE_URL_FOLDER = f"mysql+mysqlconnector://root:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{FOLDER_DB_NAME}"

folder_engine = create_engine(SQLALCHEMY_DATABASE_URL_FOLDER, echo=False)
folder_SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=folder_engine)

class folder_Base(DeclarativeBase):
    pass

def get_folderdb():
    db = folder_SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_folderdb():
    folder_Base.metadata.create_all(bind=folder_engine)