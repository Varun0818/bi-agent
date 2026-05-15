import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.chat import router as chat_router
from api.history import router as history_router
from api.schema import router as schema_router
from api.sessions import router as sessions_router
from api.traces import router as traces_router
from db.database import Base, app_engine
from services.schema_service import schema_service

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    import db.models  # noqa: F401
    from sqlalchemy import inspect, text

    # -----------------------------------
    # Fix old assistant_results schema
    # -----------------------------------

    insp = inspect(app_engine)

    if insp.has_table("assistant_results"):
        existing_cols = {
            col["name"]
            for col in insp.get_columns("assistant_results")
        }

        if "session_id" not in existing_cols:
            with app_engine.connect() as conn:
                conn.execute(text("DROP TABLE assistant_results"))
                conn.commit()

    # -----------------------------------
    # Create all tables
    # -----------------------------------

    Base.metadata.create_all(bind=app_engine)

    # -----------------------------------
    # Embed schema
    # -----------------------------------

    schema_service.embed_schema()

    # -----------------------------------
    # Cleanup garbage sessions
    # -----------------------------------

    from db.database import SessionLocal as _SL
    from db import crud as _crud

    _db = _SL()

    try:
        cleaned = _crud.cleanup_garbage_sessions(_db)

        if cleaned > 0:
            print(f"🧹 Cleaned {cleaned} garbage sessions on startup")

    finally:
        _db.close()

    print("✅ BI Agent ready")

    yield


# -----------------------------------
# FastAPI App
# -----------------------------------

app = FastAPI(
    title="BI Agent API",
    version="1.0.0",
    lifespan=lifespan
)

# -----------------------------------
# CORS Middleware
# -----------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------
# Health Endpoint
# -----------------------------------

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "app": "BI Agent API",
        "version": "1.0.0",
    }

# -----------------------------------
# Routers
# -----------------------------------

app.include_router(sessions_router, prefix="/api/v1")
app.include_router(chat_router, prefix="/api/v1")
app.include_router(history_router, prefix="/api/v1")
app.include_router(traces_router, prefix="/api/v1")
app.include_router(schema_router, prefix="/api/v1")

# -----------------------------------
# Root Endpoint
# -----------------------------------

@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "BI Agent API"
    }