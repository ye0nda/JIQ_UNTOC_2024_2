from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from folder.folder_router import router as folder_router
from file.file_router import router as file_router
from quiz.quiz_router import router as quiz_router
from user.user_router import router as user_router
from database import init_databases

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 필요시 허용할 도메인 지정
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(folder_router, prefix="/folder", tags=["folder"])
app.include_router(file_router, prefix="/file", tags=["file"])
app.include_router(quiz_router, prefix="/quiz", tags=["quiz"])
app.include_router(user_router, prefix="/user", tags=["user"])

@app.on_event("startup")
def on_startup():
    init_databases()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)