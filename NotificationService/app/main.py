# NotificationService/app/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import signal
import sys

from app.utils.consul_client import ConsulClient

app = FastAPI(title="Notification Service")
consul_client = ConsulClient()

class Notification(BaseModel):
    user_id: int
    message: str

@app.on_event("startup")
async def startup_event():
    """Register with Consul on startup"""
    consul_client.register_service(
        name="notification-service",
        port=8081,  # Using a different port than ToDoApp
        tags=["notification", "api"]
    )

@app.on_event("shutdown")
async def shutdown_event():
    """Deregister from Consul on shutdown"""
    consul_client.deregister_service()

@app.get("/health")
def health_check():
    """Health check endpoint for Consul"""
    return {"status": "healthy"}

@app.get("/api/notifications")
def get_notifications():
    """Get notifications information"""
    return {
        "status": "success",
        "message": "Notification service is running",
        "endpoints": {
            "POST /api/notifications": "Send a notification (requires user_id and message)"
        }
    }

@app.post("/api/notifications")
def send_notification(notification: Notification):
    """Send a notification to a user"""
    try:
        # In a real implementation, this would send an email, SMS, etc.
        print(f"Sending notification to user {notification.user_id}: {notification.message}")
        return {"status": "success", "notification": notification.dict()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Signal handler for graceful shutdown
def signal_handler(sig, frame):
    print("Shutting down...")
    consul_client.deregister_service()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8081, reload=True)