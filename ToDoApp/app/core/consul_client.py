# ToDoApp/app/core/consul_client.py
import consul
from typing import Any, Dict, Optional, List
from app.core.config import settings
import socket


class ConsulClient:
    def __init__(self):
        self.consul = consul.Consul(
            host=settings.CONSUL_HOST,
            port=settings.CONSUL_PORT
        )
        self.service_id = None

    def register_service(self, name: str, port: int, tags: list = None):
        """Register the service with Consul"""
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)

        self.service_id = f"{name}-{hostname}-{port}"

        # Register service with Consul
        self.consul.agent.service.register(
            name=name,
            service_id=self.service_id,
            address=ip_address,
            port=port,
            tags=tags or [],
            check={
                "http": f"http://{ip_address}:{port}/health",
                "interval": "10s",
                "timeout": "5s"
            }
        )

        print(f"Registered service {name} with Consul")

    def deregister_service(self):
        """Deregister the service from Consul"""
        if self.service_id:
            self.consul.agent.service.deregister(self.service_id)
            print(f"Deregistered service {self.service_id} from Consul")

    def get_config(self, key: str, default: Any = None) -> Any:
        """Get a configuration value from Consul KV store"""
        index, data = self.consul.kv.get(key)
        if data and data['Value']:
            return data['Value'].decode('utf-8')
        return default

    def put_config(self, key: str, value: str) -> bool:
        """Put a configuration value in Consul KV store"""
        return self.consul.kv.put(key, value)

    def get_service(self, service_name: str) -> Optional[Dict]:
        """Get a single service instance by name"""
        index, services = self.consul.catalog.service(service_name)
        if services:
            return services[0]  # Return the first instance found
        return None

    def get_service_address(self, service_name: str) -> Optional[str]:
        """Get the address of a service in the format 'host:port'"""
        service = self.get_service(service_name)
        if service:
            return f"{service['ServiceAddress']}:{service['ServicePort']}"
        return None

    def get_all_services(self) -> List[Dict]:
        """Get all registered services"""
        index, services = self.consul.catalog.services()
        result = []
        for service_name in services:
            index, instances = self.consul.catalog.service(service_name)
            result.extend(instances)
        return result