# ToDoApp/app/utils/notification_client.py
import requests
import os
from app.core.consul_client import ConsulClient


class NotificationClient:
    def __init__(self, consul_client: ConsulClient):
        self.consul_client = consul_client
        self.service_name = "notification-service"

        # Path to SSL certificates
        self.cert_path = "/etc/ssl/certs"
        self.client_cert = (
            os.path.join(self.cert_path, "client.crt"),
            os.path.join(self.cert_path, "client.key")
        )
        self.ca_cert = os.path.join(self.cert_path, "ca.crt")

    def get_service_url(self):
        """Get the URL of the notification service"""
        # Use the sidecar address instead of direct service
        address = self.consul_client.get_service_address("notification-sidecar")
        if not address:
            # Fallback to notification service if sidecar isn't registered
            address = self.consul_client.get_service_address(self.service_name)
            if not address:
                raise Exception(f"Could not find {self.service_name} or its sidecar in Consul")
        return f"https://{address}"

    def send_notification(self, user_id: int, message: str):
        """Send a notification to a user using mTLS"""
        try:
            url = f"{self.get_service_url()}/api/notifications"

            # Use mTLS with client certificate and CA certificate
            response = requests.post(
                url,
                json={"user_id": user_id, "message": message},
                cert=self.client_cert,
                verify=self.ca_cert
            )

            return response.json()
        except Exception as e:
            print(f"Failed to send notification: {e}")
            return None