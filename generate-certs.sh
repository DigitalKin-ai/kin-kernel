#!/bin/bash

# Définir les variables
CERTS_DIR="certs"
CA_KEY="$CERTS_DIR/ca_key.pem"
CA_CERT="$CERTS_DIR/ca_cert.pem"
SERVER_KEY="$CERTS_DIR/server_key.pem"
SERVER_CSR="$CERTS_DIR/server.csr"
SERVER_CERT="$CERTS_DIR/server_cert.pem"
CLIENT_KEY="$CERTS_DIR/client_key.pem"
CLIENT_CSR="$CERTS_DIR/client.csr"
CLIENT_CERT="$CERTS_DIR/client_cert.pem"
DAYS_VALID=365
SUBJECT="/C=FR/ST=Auvergne-Rhone-Alpes/L=Lyon/O=MonOrganisation/OU=IT/CN=localhost"

# Créer le répertoire certs s'il n'existe pas
mkdir -p $CERTS_DIR

# Fonction pour générer une clé privée et un certificat
generate_cert() {
    local KEY=$1
    local CSR=$2
    local CERT=$3
    local CN=$4

    # Générer une clé privée
    openssl genrsa -out $KEY 2048

    # Générer une demande de signature de certificat (CSR)
    openssl req -new -key $KEY -out $CSR -subj "$SUBJECT/CN=$CN"

    # Signer le certificat avec la CA
    openssl x509 -req -in $CSR -CA $CA_CERT -CAkey $CA_KEY -CAcreateserial -out $CERT -days $DAYS_VALID
}

# Créer l'autorité de certification (CA)
openssl genrsa -out $CA_KEY 2048
openssl req -x509 -new -nodes -key $CA_KEY -sha256 -days $DAYS_VALID -out $CA_CERT -subj "$SUBJECT/CN=RootCA"

# Générer le certificat du serveur
generate_cert $SERVER_KEY $SERVER_CSR $SERVER_CERT "localhost"

# Générer le certificat client (optionnel, décommentez si nécessaire)
# generate_cert $CLIENT_KEY $CLIENT_CSR $CLIENT_CERT "client"

# Nettoyer les fichiers temporaires
rm $CERTS_DIR/*.csr

echo "Génération des certificats terminée !"
echo "Fichiers générés dans le répertoire $CERTS_DIR :"
echo "- Autorité de certification : ca_cert.pem, ca_key.pem"
echo "- Serveur : server_cert.pem, server_key.pem"