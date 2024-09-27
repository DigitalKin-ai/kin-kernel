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
OPENSSL_CNF = $(CERT_DIR)/openssl.cnf

all: $(CA_CERT) $(SERVER_CERT) $(CLIENT_CERT)

$(CERT_DIR):
	mkdir -p $(CERT_DIR)

$(OPENSSL_CNF): | $(CERT_DIR)
	echo "[req]" > $(OPENSSL_CNF)
	echo "distinguished_name = req_distinguished_name" >> $(OPENSSL_CNF)
	echo "x509_extensions = v3_req" >> $(OPENSSL_CNF)
	echo "prompt = no" >> $(OPENSSL_CNF)
	echo "[req_distinguished_name]" >> $(OPENSSL_CNF)
	echo "C = FR" >> $(OPENSSL_CNF)
	echo "ST = Ile-de-France" >> $(OPENSSL_CNF)
	echo "L = Paris" >> $(OPENSSL_CNF)
	echo "O = MonOrganisation" >> $(OPENSSL_CNF)
	echo "OU = MonDepartement" >> $(OPENSSL_CNF)
	echo "CN = localhost" >> $(OPENSSL_CNF)
	echo "[v3_req]" >> $(OPENSSL_CNF)
	echo "keyUsage = critical, digitalSignature, keyEncipherment" >> $(OPENSSL_CNF)
	echo "extendedKeyUsage = serverAuth, clientAuth" >> $(OPENSSL_CNF)
	echo "subjectAltName = @alt_names" >> $(OPENSSL_CNF)
	echo "[alt_names]" >> $(OPENSSL_CNF)
	echo "DNS.1 = localhost" >> $(OPENSSL_CNF)
	echo "IP.1 = 127.0.0.1" >> $(OPENSSL_CNF)

$(CA_KEY): | $(CERT_DIR)
	openssl genrsa -out $(CA_KEY) 4096

$(CA_CERT): $(CA_KEY) $(OPENSSL_CNF)
	openssl req -x509 -new -nodes -key $(CA_KEY) -sha256 -days 1024 -out $(CA_CERT) -config $(OPENSSL_CNF)

$(SERVER_KEY): | $(CERT_DIR)
	openssl genrsa -out $(SERVER_KEY) 2048

$(SERVER_CSR): $(SERVER_KEY) $(OPENSSL_CNF)
	openssl req -new -key $(SERVER_KEY) -out $(SERVER_CSR) -config $(OPENSSL_CNF)

$(SERVER_CERT): $(SERVER_CSR) $(CA_CERT) $(CA_KEY) $(OPENSSL_CNF)
	openssl x509 -req -in $(SERVER_CSR) -CA $(CA_CERT) -CAkey $(CA_KEY) -CAcreateserial -out $(SERVER_CERT) -days 365 -sha256 -extfile $(OPENSSL_CNF) -extensions v3_req

$(CLIENT_KEY): | $(CERT_DIR)
	openssl genrsa -out $(CLIENT_KEY) 2048

$(CLIENT_CSR): $(CLIENT_KEY) $(OPENSSL_CNF)
	openssl req -new -key $(CLIENT_KEY) -out $(CLIENT_CSR) -config $(OPENSSL_CNF)

$(CLIENT_CERT): $(CLIENT_CSR) $(CA_CERT) $(CA_KEY) $(OPENSSL_CNF)
	openssl x509 -req -in $(CLIENT_CSR) -CA $(CA_CERT) -CAkey $(CA_KEY) -CAcreateserial -out $(CLIENT_CERT) -days 365 -sha256 -extfile $(OPENSSL_CNF) -extensions v3_req

clean:
	rm -rf $(CERT_DIR)

.PHONY: all clean