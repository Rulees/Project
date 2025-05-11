#!/bin/sh

echo "🔍 SA_KEY_FILE=$SA_KEY_FILE"
echo "🔍 DOMAIN=$DOMAIN"
echo "🔍 CERTIFICATE_ID=$CERTIFICATE_ID"

CERT_PATH="/etc/letsencrypt/live/$DOMAIN"
YC_API_URL="https://data.certificate-manager.api.cloud.yandex.net/certificate-manager/v1/certificates/${CERTIFICATE_ID}:getContent"

# 🧪 Сначала проверим: есть ли уже сертификаты
if [ -s "$CERT_PATH/fullchain.pem" ] && [ -s "$CERT_PATH/privkey.pem" ]; then
    echo "✅ Certificates already exist. Using them."
else
    echo "🔄 Certificates missing. Downloading new ones..."

    if [ -n "$SA_KEY_FILE" ] && [ -f "$SA_KEY_FILE" ]; then
        echo "🔐 Getting IAM token via yandexcloud SDK..."

        # Получение IAM токена
        IAM_TOKEN=$(python3 - <<EOF
import time, json, jwt, sys
from yandexcloud import SDK
from yandex.cloud.iam.v1.iam_token_service_pb2 import CreateIamTokenRequest
from yandex.cloud.iam.v1.iam_token_service_pb2_grpc import IamTokenServiceStub

try:
    with open("$SA_KEY_FILE") as f:
        key_data = json.load(f)

    private_key = key_data['private_key']
    key_id = key_data['id']
    sa_id = key_data['service_account_id']

    now = int(time.time())
    payload = {
        'aud': 'https://iam.api.cloud.yandex.net/iam/v1/tokens',
        'iss': sa_id,
        'iat': now,
        'exp': now + 3600
    }

    jwt_token = jwt.encode(payload, private_key, algorithm='PS256', headers={'kid': key_id})
    sdk = SDK()
    iam = sdk.client(IamTokenServiceStub)
    token = iam.Create(CreateIamTokenRequest(jwt=jwt_token))
    print(token.iam_token)

except Exception as e:
    print("❌ Python error:", str(e), file=sys.stderr)
    exit(1)
EOF
)

    if [ -z "$IAM_TOKEN" ] || [ "$IAM_TOKEN" = "null" ]; then
        echo "❌ Failed to get IAM token from SA key"
        exit 1
    fi
else
    echo "❌ SA_KEY_FILE is not provided or missing"
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
fi


# GENERATE FILE *.conf WITH VARS FROM .env
for file in /etc/nginx/conf.d/*.template /etc/nginx/conf.d/.*.template; do
    [ -e "$file" ] || continue
    envsubst '${DOMAIN} ${EMAIL}' < "$file" > "${file%.template}"
    rm "$file"
done


nginx &
tail -f /var/log/nginx/access.log /var/log/nginx/error.log