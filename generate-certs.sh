#!/bin/bash
# Script to generate certificates for mTLS

# Create a directory for certificates
mkdir -p certificates
cd certificates

# Generate a CA key and certificate
echo "Generating CA key and certificate..."
openssl genrsa -out ca.key 2048
openssl req -x509 -new -nodes -key ca.key -sha256 -days 1024 -out ca.crt -subj "/CN=MyCA/O=MyOrganization"

# Generate server key and CSR
echo "Generating server key and CSR..."
openssl genrsa -out server.key 2048
openssl req -new -key server.key -out server.csr -subj "/CN=server/O=MyOrganization"

# Generate client key and CSR
echo "Generating client key and CSR..."
openssl genrsa -out client.key 2048
openssl req -new -key client.key -out client.csr -subj "/CN=client/O=MyOrganization"

# Create config for SAN (Subject Alternative Name)
cat > openssl_ext.cnf << EOF
[req]
req_extensions = v3_req
distinguished_name = req_distinguished_name

[req_distinguished_name]

[v3_req]
subjectAltName = @alt_names

[alt_names]
DNS.1 = localhost
DNS.2 = kong
DNS.3 = todoapp
DNS.4 = notification-service
DNS.5 = todoapp-sidecar
DNS.6 = notification-sidecar
IP.1 = 127.0.0.1
EOF

# Sign the server certificate
echo "Signing server certificate..."
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt -days 365 -extfile openssl_ext.cnf -extensions v3_req

# Sign the client certificate
echo "Signing client certificate..."
openssl x509 -req -in client.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out client.crt -days 365 -extfile openssl_ext.cnf -extensions v3_req

# Clean up CSR files
rm *.csr

echo "Certificate generation complete!"
echo "CA certificate: ca.crt"
echo "CA key: ca.key"
echo "Server certificate: server.crt"
echo "Server key: server.key"
echo "Client certificate: client.crt"
echo "Client key: client.key"

# Return to the original directory
cd ..