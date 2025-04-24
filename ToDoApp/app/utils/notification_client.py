# ToDoApp/app/utils/notification_client.py
import requests
from app.core.consul_client import ConsulClient


class NotificationClient:
    def __init__(self, consul_client: ConsulClient):
        self.consul_client = consul_client
        self.service_name = "notification-service"

    def get_service_url(self):
        """Get the URL of the notification service"""
        address = self.consul_client.get_service_address(self.service_name)
        if not address:
            raise Exception(f"Could not find {self.service_name} in Consul")
        return f"http://{address}"

    def send_notification(self, user_id: int, message: str):
        """Send a notification to a user"""
        try:
            url = f"{self.get_service_url()}/api/notifications"
            response = requests.post(
                url,
                json={"user_id": user_id, "message": message}
            )
            return response.json()
        except Exception as e:
            print(f"Failed to send notification: {e}")
            return None