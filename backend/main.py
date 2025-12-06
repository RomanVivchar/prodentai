"""
ProDentAI Backend API
FastAPI application with all endpoints
"""

import importlib.util
import logging
import os
import sys
import time

import uvicorn
from database import get_db, init_db
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer

# Load environment variables FIRST, before importing MLServiceManager
load_dotenv()

# Настройка подробного логирования
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FORMAT = (
    "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"
)

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format=LOG_FORMAT,
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)

# Создаем логгер для приложения
logger = logging.getLogger(__name__)
logger.info("Logging configured with level: %s", LOG_LEVEL)

# Импорт shared модулей - проверяем разные пути ПЕРЕД импортом роутеров
# В Docker: /app - это WORKDIR (соответствует ./backend на хосте)
# /shared - это volume (соответствует ./shared на хосте)
if os.path.exists("/shared"):
    # Docker: volume монтируется в /shared
    sys.path.insert(0, "/shared")
    import types

    if "shared" not in sys.modules:
        shared_module = types.ModuleType("shared")
        sys.modules["shared"] = shared_module

    spec = importlib.util.spec_from_file_location(
        "ml_services", "/shared/ml_services.py"
    )
    ml_services = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ml_services)
    sys.modules["ml_services"] = ml_services
    sys.modules["shared"].ml_services = ml_services
    MLServiceManager = ml_services.MLServiceManager
else:
    # Локальная разработка
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from shared.ml_services import MLServiceManager

from routers import (
    auth,
    facts,
    nutrition,
    psychology,
    reminders,
    risk_assessment,
    users,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

# Initialize FastAPI app
app = FastAPI(
    title="ProDentAI API",
    description="Персональный ИИ-компаньон для стоматологического здоровья",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


# Middleware для логирования запросов
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Логирование всех HTTP запросов"""
    start_time = time.time()

    # Логируем входящий запрос
    client_host = request.client.host if request.client else "unknown"
    logger.info(
        "→ %s %s | Client: %s | Query: %s",
        request.method,
        request.url.path,
        client_host,
        dict(request.query_params),
    )

    # Логируем заголовки (без чувствительных данных)
    headers_to_log = {
        k: v
        for k, v in request.headers.items()
        if k.lower() not in ["authorization", "cookie"]
    }
    logger.debug("Request headers: %s", headers_to_log)

    try:
        response = await call_next(request)
        process_time = time.time() - start_time

        # Логируем ответ
        logger.info(
            "← %s %s | Status: %d | Time: %.3fs",
            request.method,
            request.url.path,
            response.status_code,
            process_time,
        )

        return response
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            "✗ %s %s | Error: %s | Time: %.3fs",
            request.method,
            request.url.path,
            str(e),
            process_time,
            exc_info=True,
        )
        raise


# CORS middleware
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS", "https://prodentai.tech,http://prodentai.tech"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Initialize ML services
ml_manager = MLServiceManager()

# Global exception handlers
from fastapi import Request


@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    """Handle database integrity errors"""
    return JSONResponse(
        status_code=400,
        content={"detail": "Data integrity error. The record may already exist."},
    )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """Handle value errors"""
    return JSONResponse(status_code=400, content={"detail": str(exc)})


# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(
    risk_assessment.router, prefix="/api/risks", tags=["Risk Assessment"]
)
app.include_router(nutrition.router, prefix="/api/nutrition", tags=["Nutrition"])
app.include_router(psychology.router, prefix="/api/psychology", tags=["Psychology"])
app.include_router(reminders.router, prefix="/api/reminders", tags=["Reminders"])
app.include_router(facts.router, prefix="/api/facts", tags=["Facts"])


@app.on_event("startup")
async def startup_event():
    """Initialize database and ML models on startup"""
    import logging

    logging.basicConfig(level=logging.INFO)

    # Сначала создаем таблицы (если их нет)
    await init_db()
    logger.info("Database tables created/verified")

    # Затем запускаем миграции (для добавления недостающих колонок в существующие таблицы)
    try:
        from migrate_db import migrate_database
        await migrate_database()
        logger.info("Database migrations completed")
    except Exception as e:
        logger.warning(f"Migration check failed (may be expected): {e}")
    await ml_manager.initialize_models()

    # Log ML service status
    if ml_manager.client:
        logging.info(
            f"✅ ML Service initialized with OpenAI API (model: {ml_manager.model_name})"
        )
    else:
        logging.warning("⚠️ ML Service not configured - using fallback responses")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "ProDentAI API is running",
        "version": "1.0.0",
        "status": "healthy",
    }


@app.get("/api/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """Detailed health check"""
    try:
        # Check database connection
        from sqlalchemy import text
        await db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"

    try:
        # Check Redis connection (if needed)
        import redis.asyncio as aioredis

        # In Docker: use "redis://redis:6379" (service name)
        # Locally: use "redis://localhost:6379"
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        redis_client = aioredis.from_url(redis_url)
        await redis_client.ping()
        await redis_client.close()
        redis_status = "connected"
    except Exception as e:
        redis_status = f"error: {str(e)}"

    return {
        "status": "healthy",
        "database": db_status,
        "redis": redis_status,
        "ml_service": "initialized" if ml_manager.client else "not_configured",
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
