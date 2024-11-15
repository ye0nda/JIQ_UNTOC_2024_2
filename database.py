from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from dotenv import load_dotenv
import os

DB_HOST = os.environ.get("DB_HOST")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
FOLDER_DB_NAME = os.environ.get("FOLDER_DB_NAME")
DB_PORT = os.environ.get("DB_PORT", 3306)

SQLALCHEMY_DATABASE_URL_FOLDER = f"mysql+mysqlconnector://root:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{FOLDER_DB_NAME}"

folder_engine = create_engine(SQLALCHEMY_DATABASE_URL_FOLDER)

folder_SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=folder_engine)

folder_Base = declarative_base()

def get_folderdb():
    db = folder_SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_folderdb():
    folder_Base.metadata.create_all(bind=folder_engine)