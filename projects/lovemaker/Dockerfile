FROM nginx:1.27.4-alpine

EXPOSE 80 443


ARG EMAIL
ARG DOMAIN
ARG CERTIFICATE_ID
ARG IAM_TOKEN
ARG SA_KEY_FILE

ENV EMAIL=$EMAIL
ENV DOMAIN=$DOMAIN
ENV CERTIFICATE_ID=$CERTIFICATE_ID
ENV IAM_TOKEN=$IAM_TOKEN
ENV SA_KEY_FILE=$SA_KEY_FILE

RUN apk add --no-cache python3 py3-pip py3-setuptools py3-wheel gcc musl-dev libffi-dev openssl-dev openssl lnav nano curl jq \
    && pip3 install --break-system-packages --no-cache-dir yandexcloud PyJWT cryptography grpcio


COPY nginx_serv/ /sites/starter/          
COPY nginx_conf/ /etc/nginx/
COPY entrypoint-yandex-cert.sh /entrypoint-yandex-cert.sh



RUN if ! getent group www-data; then addgroup -S www-data; fi && \
    if ! getent passwd www-data; then adduser -S www-data -G www-data; fi


VOLUME ["/etc/letsencrypt", "/certbot/www", "/sites/starter"]


RUN chmod +x /entrypoint-yandex-cert.sh


ENTRYPOINT ["/entrypoint-yandex-cert.sh"]