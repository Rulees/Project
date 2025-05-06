#!/bin/sh

CERT_PATH="/etc/letsencrypt/live/$DOMAIN"
YC_API_URL="https://data.certificate-manager.api.cloud.yandex.net/certificate-manager/v1/certificates/${CERTIFICATE_ID}:getContent"


if [ ! -f $CERT_PATH/fullchain.pem ] || [ ! -f $CERT_PATH/privkey.pem ]; then
    echo "🔄 Certificates missing. Downloading new ones..."

    if [ -z "$IAM_TOKEN" ]; then
        echo "❌ Error: IAM token is empty!"
        exit 1
    fi

    mkdir -p $CERT_PATH

    # GET CERTS FROM YC
    CERT_RESPONSE=$(curl -s -H "Authorization: Bearer $IAM_TOKEN" -H "Content-Type: application/json" "$YC_API_URL")

    # CHECK FOR CORRECT API_RESPONSE & $API_TOKEN
    if ! echo "$CERT_RESPONSE" | jq -e .certificateChain >/dev/null 2>&1; then
        echo "❌ Error: Incorrect IAM_TOKEN or API response is not valid JSON! Response: $CERT_RESPONSE"
        exit 1
    fi

    # WRITE CERT
    echo "$CERT_RESPONSE" | jq -r '.certificateChain[]' > "$CERT_PATH/fullchain.pem"
    echo "$CERT_RESPONSE" | jq -r '.privateKey // empty' > "$CERT_PATH/privkey.pem"

    # CHECK FOR CERT PRESENCE
    if [ -z "$(cat "$CERT_PATH/fullchain.pem")" ] || [ -z "$(cat "$CERT_PATH/privkey.pem")" ]; then
        echo "❌ Error: Retrieved certificates are empty!"
        exit 1
    fi

    echo "✅ Certificates downloaded."
else
    echo "✅ Certificates already exist. Using them."
fi


# GENERATE FILE *.conf WITH VARS FROM .env
for file in /etc/nginx/conf.d/*.template; do
    envsubst '${DOMAIN} ${EMAIL}' < "$file" > "${file%.template}"
    rm "$file"
done


nginx &
tail -f /var/log/nginx/access.log /var/log/nginx/error.log