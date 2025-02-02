from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from folder.folder_router import router as folder_router
from quiz.quiz_router import router as quiz_router
from retry.retry_router import router as retry_router
from database import init_databases

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 필요시 허용할 도메인 지정
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(folder_router, prefix="/folder", tags=["folder"])
app.include_router(quiz_router, prefix="/quiz", tags=["quiz"])
app.include_router(retry_router, prefix="/retry", tags=["retry"])

@app.on_event("startup")
def on_startup():
    init_databases()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)