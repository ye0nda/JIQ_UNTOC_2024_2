from fastapi import APIRouter, HTTPException, UploadFile, File
import os
import shutil

router = APIRouter(prefix="/file", tags=["file"])

UPLOAD_DIR = "uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)  # 업로드 디렉터리 생성


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    파일을 업로드하고 경로를 반환합니다.
    """
    try:
        # 파일 저장
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return {"message": "File uploaded successfully", "file_path": file_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
