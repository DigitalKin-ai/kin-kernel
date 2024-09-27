# Makefile pour générer des certificats TLS/mTLS similaires à AWS

CERT_DIR = certs
CA_KEY = $(CERT_DIR)/ca.key
CA_CERT = $(CERT_DIR)/ca.crt
SERVER_KEY = $(CERT_DIR)/server.key
SERVER_CSR = $(CERT_DIR)/server.csr
SERVER_CERT = $(CERT_DIR)/server.crt
CLIENT_KEY = $(CERT_DIR)/client.key
CLIENT_CSR = $(CERT_DIR)/client.csr
CLIENT_CERT = $(CERT_DIR)/client.crt
CA_OPENSSL_CNF = $(CERT_DIR)/ca_openssl.cnf
SERVER_OPENSSL_CNF = $(CERT_DIR)/server_openssl.cnf
CLIENT_OPENSSL_CNF = $(CERT_DIR)/client_openssl.cnf

all: $(CA_CERT) $(SERVER_CERT) $(CLIENT_CERT)

$(CERT_DIR):
	mkdir -p $(CERT_DIR)

$(CA_OPENSSL_CNF): | $(CERT_DIR)
	echo "[req]" > $(CA_OPENSSL_CNF)
	echo "distinguished_name = req_distinguished_name" >> $(CA_OPENSSL_CNF)
	echo "x509_extensions = v3_ca" >> $(CA_OPENSSL_CNF)
	echo "prompt = no" >> $(CA_OPENSSL_CNF)
	echo "[req_distinguished_name]" >> $(CA_OPENSSL_CNF)
	echo "C = FR" >> $(CA_OPENSSL_CNF)
	echo "ST = Ile-de-France" >> $(CA_OPENSSL_CNF)
	echo "L = Paris" >> $(CA_OPENSSL_CNF)
	echo "O = MonOrganisation" >> $(CA_OPENSSL_CNF)
	echo "OU = MonDepartement" >> $(CA_OPENSSL_CNF)
	echo "CN = MonCA" >> $(CA_OPENSSL_CNF)
	echo "[v3_ca]" >> $(CA_OPENSSL_CNF)
	echo "subjectKeyIdentifier = hash" >> $(CA_OPENSSL_CNF)
	echo "authorityKeyIdentifier = keyid:always,issuer" >> $(CA_OPENSSL_CNF)
	echo "basicConstraints = critical, CA:true" >> $(CA_OPENSSL_CNF)
	echo "keyUsage = critical, digitalSignature, cRLSign, keyCertSign" >> $(CA_OPENSSL_CNF)

$(SERVER_OPENSSL_CNF): | $(CERT_DIR)
	echo "[req]" > $(SERVER_OPENSSL_CNF)
	echo "distinguished_name = req_distinguished_name" >> $(SERVER_OPENSSL_CNF)
	echo "x509_extensions = v3_req" >> $(SERVER_OPENSSL_CNF)
	echo "prompt = no" >> $(SERVER_OPENSSL_CNF)
	echo "[req_distinguished_name]" >> $(SERVER_OPENSSL_CNF)
	echo "C = FR" >> $(SERVER_OPENSSL_CNF)
	echo "ST = Ile-de-France" >> $(SERVER_OPENSSL_CNF)
	echo "L = Paris" >> $(SERVER_OPENSSL_CNF)
	echo "O = MonOrganisation" >> $(SERVER_OPENSSL_CNF)
	echo "OU = MonDepartement" >> $(SERVER_OPENSSL_CNF)
	echo "CN = localhost" >> $(SERVER_OPENSSL_CNF)
	echo "[v3_req]" >> $(SERVER_OPENSSL_CNF)
	echo "basicConstraints = CA:FALSE" >> $(SERVER_OPENSSL_CNF)
	echo "keyUsage = critical, digitalSignature, keyEncipherment" >> $(SERVER_OPENSSL_CNF)
	echo "extendedKeyUsage = serverAuth, clientAuth" >> $(SERVER_OPENSSL_CNF)
	echo "subjectAltName = @alt_names" >> $(SERVER_OPENSSL_CNF)
	echo "[alt_names]" >> $(SERVER_OPENSSL_CNF)
	echo "DNS.1 = localhost" >> $(SERVER_OPENSSL_CNF)
	echo "IP.1 = 127.0.0.1" >> $(SERVER_OPENSSL_CNF)
	echo "IP.2 = ::1" >> $(SERVER_OPENSSL_CNF)
	echo "URI.1 = localhost:50051" >> $(SERVER_OPENSSL_CNF)
	echo "URI.2 = localhost:50052" >> $(SERVER_OPENSSL_CNF)
	echo "URI.3 = localhost:50053" >> $(SERVER_OPENSSL_CNF)
	echo "URI.4 = localhost:50054" >> $(SERVER_OPENSSL_CNF)
	echo "URI.5 = localhost:50055" >> $(SERVER_OPENSSL_CNF)

$(CLIENT_OPENSSL_CNF): | $(CERT_DIR)
	echo "[req]" > $(CLIENT_OPENSSL_CNF)
	echo "distinguished_name = req_distinguished_name" >> $(CLIENT_OPENSSL_CNF)
	echo "x509_extensions = v3_req" >> $(CLIENT_OPENSSL_CNF)
	echo "prompt = no" >> $(CLIENT_OPENSSL_CNF)
	echo "[req_distinguished_name]" >> $(CLIENT_OPENSSL_CNF)
	echo "C = FR" >> $(CLIENT_OPENSSL_CNF)
	echo "ST = Ile-de-France" >> $(CLIENT_OPENSSL_CNF)
	echo "L = Paris" >> $(CLIENT_OPENSSL_CNF)
	echo "O = MonOrganisation" >> $(CLIENT_OPENSSL_CNF)
	echo "OU = MonDepartement" >> $(CLIENT_OPENSSL_CNF)
	echo "CN = client" >> $(CLIENT_OPENSSL_CNF)
	echo "[v3_req]" >> $(CLIENT_OPENSSL_CNF)
	echo "basicConstraints = CA:FALSE" >> $(CLIENT_OPENSSL_CNF)
	echo "keyUsage = critical, digitalSignature, keyEncipherment" >> $(CLIENT_OPENSSL_CNF)
	echo "extendedKeyUsage = clientAuth" >> $(CLIENT_OPENSSL_CNF)

$(CA_KEY): | $(CERT_DIR)
	openssl genrsa -out $(CA_KEY) 4096

$(CA_CERT): $(CA_KEY) $(CA_OPENSSL_CNF)
	openssl req -x509 -new -nodes -key $(CA_KEY) -sha256 -days 1024 -out $(CA_CERT) -config $(CA_OPENSSL_CNF) -extensions v3_ca

$(SERVER_KEY): | $(CERT_DIR)
	openssl genrsa -out $(SERVER_KEY) 2048

$(SERVER_CSR): $(SERVER_KEY) $(SERVER_OPENSSL_CNF)
	openssl req -new -key $(SERVER_KEY) -out $(SERVER_CSR) -config $(SERVER_OPENSSL_CNF)

$(SERVER_CERT): $(SERVER_CSR) $(CA_CERT) $(CA_KEY) $(SERVER_OPENSSL_CNF)
	openssl x509 -req -in $(SERVER_CSR) -CA $(CA_CERT) -CAkey $(CA_KEY) -CAcreateserial -out $(SERVER_CERT) -days 365 -sha256 -extfile $(SERVER_OPENSSL_CNF) -extensions v3_req

$(CLIENT_KEY): | $(CERT_DIR)
	openssl genrsa -out $(CLIENT_KEY) 2048

$(CLIENT_CSR): $(CLIENT_KEY) $(CLIENT_OPENSSL_CNF)
	openssl req -new -key $(CLIENT_KEY) -out $(CLIENT_CSR) -config $(CLIENT_OPENSSL_CNF)

$(CLIENT_CERT): $(CLIENT_CSR) $(CA_CERT) $(CA_KEY) $(CLIENT_OPENSSL_CNF)
	openssl x509 -req -in $(CLIENT_CSR) -CA $(CA_CERT) -CAkey $(CA_KEY) -CAcreateserial -out $(CLIENT_CERT) -days 365 -sha256 -extfile $(CLIENT_OPENSSL_CNF) -extensions v3_req

clean:
	rm -rf $(CERT_DIR)

.PHONY: all clean