from fastapi import FastAPI
from sqlalchemy import text

from app.database import engine

app = FastAPI(
    title="WorkFlow AI API",
    version="1.0.0"
)


@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "WorkFlow AI API funcionando"
    }


@app.get("/health")
def health():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "status": "ok",
            "database": "connected"
        }

    except Exception as e:
        return {
            "status": "error",
            "database": "disconnected",
            "detail": str(e)
        }