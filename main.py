from fastapi import FastAPI
from folder.folder_router import router as folder_router
from database import init_folderdb

app = FastAPI()

app.include_router(folder_router, prefix="/folder", tags=["folder"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)