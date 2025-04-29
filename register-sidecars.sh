#!/bin/sh
# Script to register sidecars with Consul service discovery

# Wait for Consul to be ready
echo "Waiting for Consul to be ready..."
until curl --output /dev/null --silent --fail http://consul:8500/v1/status/leader; do
    printf '.'
    sleep 5
done
echo "Consul is ready!"

# Wait for the services to start up
echo "Waiting for services to start..."
sleep 10

# First, check if the actual services are running
echo "Checking if TodoApp is available..."
until curl --output /dev/null --silent --fail http://todoapp:8080/health; do
    printf '.'
    sleep 2
done
echo "TodoApp is running!"

echo "Checking if Notification Service is available..."
until curl --output /dev/null --silent --fail http://notification-service:8081/health; do
    printf '.'
    sleep 2
done
echo "Notification Service is running!"

# Now wait for sidecars to be ready
echo "Checking if TodoApp sidecar is available..."
until curl --output /dev/null --silent --fail http://todoapp-sidecar:10000; do
    printf '.'
    sleep 2
done
echo "TodoApp sidecar is running!"

echo "Checking if Notification sidecar is available..."
until curl --output /dev/null --silent --fail http://notification-sidecar:10001; do
    printf '.'
    sleep 2
done
echo "Notification sidecar is running!"

# Register TodoApp sidecar with HTTP health check
echo "Registering TodoApp sidecar with Consul..."
curl -X PUT -d '{
  "ID": "todoapp-sidecar",
  "Name": "todoapp-sidecar",
  "Address": "todoapp-sidecar",
  "Port": 10000,
  "Tags": ["proxy", "sidecar", "todoapp"],
  "Check": {
    "HTTP": "http://todoapp-sidecar:10000/",
    "Interval": "10s",
    "Timeout": "5s"
  }
}' http://consul:8500/v1/agent/service/register

# Register Notification sidecar with HTTP health check
echo "Registering Notification sidecar with Consul..."
curl -X PUT -d '{
  "ID": "notification-sidecar",
  "Name": "notification-sidecar",
  "Address": "notification-sidecar",
  "Port": 10001,
  "Tags": ["proxy", "sidecar", "notification"],
  "Check": {
    "HTTP": "http://notification-sidecar:10001/",
    "Interval": "10s",
    "Timeout": "5s"
  }
}' http://consul:8500/v1/agent/service/register

echo "Sidecar registration complete!"