from fastapi import FastAPI
from sqlalchemy import text

from app.core.database import engine

app = FastAPI(
    title="AI Helpdesk API",
    version="1.0.0",
)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "ai-helpdesk-api",
    }

@app.get("/health/db")
def health_check_db():
    with engine.connect() as connection:
        database_name = connection.scalar(
            text("SELECT current_database()")
            )
    return {
        "status": "ok",
        "database": database_name,
    }