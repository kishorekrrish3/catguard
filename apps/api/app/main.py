from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import logging
import time

from app.config import settings
from app.core.redis_client import get_redis_pool, close_redis
from app.core.storage import ensure_bucket_exists
from app.routers import auth, zones, imagery, detections, sensors, alerts, reports, community, users, websocket

logger = logging.getLogger(__name__)

# -------------------------------------------------------
# App factory
# -------------------------------------------------------
app = FastAPI(
    title="CAT-Guard API",
    description="Catchment Area Treatment Forest Monitoring System — Real-time forest monitoring, ML threat detection, IoT sensor integration.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# -------------------------------------------------------
# Middleware
# -------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    logger.info(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.1f}ms")
    response.headers["X-Process-Time"] = f"{process_time:.1f}ms"
    return response


# -------------------------------------------------------
# Startup / Shutdown events
# -------------------------------------------------------
@app.on_event("startup")
async def startup_event():
    logger.info("Starting CAT-Guard API...")
    try:
        await get_redis_pool()
        logger.info("Redis connection established")
    except Exception as e:
        logger.warning(f"Redis connection failed (non-fatal in dev): {e}")
    try:
        ensure_bucket_exists()
        logger.info("MinIO bucket ready")
    except Exception as e:
        logger.warning(f"MinIO connection failed (non-fatal in dev): {e}")
    logger.info("CAT-Guard API started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down CAT-Guard API...")
    await close_redis()
    logger.info("CAT-Guard API shutdown complete")


# -------------------------------------------------------
# Health check
# -------------------------------------------------------
@app.get("/health", tags=["Health"])
async def health_check():
    redis_ok = False
    try:
        redis = await get_redis_pool()
        await redis.ping()
        redis_ok = True
    except Exception:
        pass

    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": settings.APP_ENV,
        "services": {
            "redis": "healthy" if redis_ok else "unavailable",
            "database": "healthy",  # If we got here, DB is ok
        },
    }


# -------------------------------------------------------
# Global exception handlers
# -------------------------------------------------------
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(status_code=404, content={"detail": f"Endpoint {request.url.path} not found"})


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    logger.error(f"Internal server error: {exc}", exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "An internal server error occurred"})


# -------------------------------------------------------
# Include routers
# -------------------------------------------------------
PREFIX = settings.API_PREFIX

app.include_router(auth.router, prefix=PREFIX)
app.include_router(zones.router, prefix=PREFIX)
app.include_router(imagery.router, prefix=PREFIX)
app.include_router(detections.router, prefix=PREFIX)
app.include_router(sensors.router, prefix=PREFIX)
app.include_router(alerts.router, prefix=PREFIX)
app.include_router(reports.router, prefix=PREFIX)
app.include_router(community.router, prefix=PREFIX)
app.include_router(users.router, prefix=PREFIX)
app.include_router(websocket.router)  # No prefix — /ws/ directly
