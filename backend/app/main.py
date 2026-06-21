import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.domains.identity.routes import auth_router, profile_router
from app.domains.content.routes.subjects import router as subjects_router

# CRITICAL FIX: Import the redis initialization functions from your database file
from app.database import init_redis, close_redis 

def parse_cors_origins(origins_var) -> list[str]:
    """Safely parse CORS origins whether it's a string, JSON string, or list."""
    if isinstance(origins_var, list):
        return origins_var
    if isinstance(origins_var, str):
        try:
            return json.loads(origins_var)
        except Exception:
            return [org.strip(' "\'') for org in origins_var.strip("[]").split(",")]
    return ["*"]

def create_app() -> FastAPI:
    """Application factory for FastAPI."""
    app = FastAPI(
        title=getattr(settings, 'APP_NAME', 'NEET POS'),
        version=getattr(settings, 'APP_VERSION', '0.1.0'),
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json"
    )

    allowed_origins = parse_cors_origins(getattr(settings, 'CORS_ORIGINS', '["*"]'))

    # CRITICAL FIX: Starlette crashes if allow_origins=["*"] and allow_credentials=True.
    # We dynamically switch to origin regex to satisfy both dev wildcard needs and security specs.
    if "*" in allowed_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[],
            allow_origin_regex=".*",
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    else:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=allowed_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Clean domain routing: attach routers securely mapping blueprint exact paths
    app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication & Identity"])
    app.include_router(profile_router, prefix="/api/v1/profile", tags=["Profile"])
    app.include_router(subjects_router, prefix="/api/v1/subjects", tags=["Content Domain - Subjects"])

    @app.get("/health/live", tags=["System Health"])
    async def liveness_check():
        return JSONResponse(content={"status": "alive"})

    @app.get("/health/ready", tags=["System Health"])
    async def readiness_check():
        return JSONResponse(content={"status": "ready"})

    @app.get("/", tags=["System Health"])
    async def root_health_check():
        return JSONResponse(content={
            "app_name": getattr(settings, 'APP_NAME', 'NEET POS'),
            "version": getattr(settings, 'APP_VERSION', '0.1.0'),
            "status": "online"
        })

    return app

app = create_app()

# ==========================================
# CRITICAL FIX: INITIALIZE REDIS ON STARTUP
# ==========================================
@app.on_event("startup")
async def startup_event():
    await init_redis()

@app.on_event("shutdown")
async def shutdown_event():
    await close_redis()