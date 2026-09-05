from fastapi import FastAPI
from sqlalchemy import text

from app.core.database import engine
from app.api.routes.tickets import router as tickets_router
from app.api.routes.ticket_comments import router as ticket_comments_router
from app.api.routes.auth import router as auth_router
from app.api.routes.knowledge_documents import router as knowledge_documents_router
from app.api.routes.knowledge_chunks import router as knowledge_chunks_router

app = FastAPI(
    title="AI Helpdesk API",
    version="1.0.0",
)

app.include_router(
    auth_router,
    prefix="/api/v1",
    )   

app.include_router(
    tickets_router,
    prefix="/api/v1",
    tags=["Tickets"],
    )

app.include_router(
    ticket_comments_router,
    prefix="/api/v1",
    tags=["Ticket Comments"],
)

app.include_router(
    knowledge_documents_router,
    prefix="/api/v1",
    tags=["Knowledge Documents"],
)

app.include_router(
    knowledge_chunks_router,
    prefix="/api/v1",
    tags=["Knowledge Chunks"],
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