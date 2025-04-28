from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database.session import engine
from app.database.base import Base
import uvicorn
import signal
import sys

from app.api.endpoints.auth import router as auth_router
from app.api.endpoints.user import router as user_router
from app.api.endpoints.task import router as task_router
from app.core.config import settings
from app.core.consul_client import ConsulClient

# Create DB tables if not existing
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(task_router)

# Create Consul client
consul_client = None
if settings.CONSUL_ENABLED:
    consul_client = ConsulClient()

@app.get("/")
def root():
    """Root endpoint"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": "TodoApp API Service",
        "endpoints": [
            "/tasks - Task management",
            "/auth - Authentication",
            "/users - User management",
            "/health - Health check"
        ]
    }

@app.on_event("startup")
async def startup_event():
    """Startup event handler - register with Consul if enabled"""
    if settings.CONSUL_ENABLED and consul_client:
        consul_client.register_service(
            name=settings.APP_NAME,
            port=settings.SERVICE_PORT,
            tags=["api", "todoapp"]
        )

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler - deregister from Consul if enabled"""
    if settings.CONSUL_ENABLED and consul_client:
        consul_client.deregister_service()

@app.get("/health")
def health():
    """Health check endpoint for Consul"""
    return {"status": "healthy"}

# Signal handler for graceful shutdown
def signal_handler(sig, frame):
    print("Shutting down...")
    if settings.CONSUL_ENABLED and consul_client:
        consul_client.deregister_service()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.SERVICE_HOST,
        port=settings.SERVICE_PORT,
        reload=True
    )