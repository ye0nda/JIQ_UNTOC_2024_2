from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from folder.folder_router import router as folder_router
from quiz.quiz_router import router as quiz_router
from file.file_router import router as file_router
from database import init_databases

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(folder_router, prefix="/folder", tags=["folder"])
app.include_router(quiz_router, prefix="/quiz", tags=["quiz"])
app.include_router(file_router, prefix="/file", tags=["file"])

@app.on_event("startup")
def on_startup():
    init_databases()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)