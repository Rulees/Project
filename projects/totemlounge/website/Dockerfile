FROM nginx:1.27.4-alpine

EXPOSE 80 443


ARG EMAIL
ARG DOMAIN
ARG CERTIFICATE_ID
ARG IAM_TOKEN

ENV EMAIL=$EMAIL
ENV DOMAIN=$DOMAIN
ENV CERTIFICATE_ID=$CERTIFICATE_ID
ENV IAM_TOKEN=$IAM_TOKEN

RUN apk add --no-cache certbot certbot-nginx python3 openssl lnav nano curl jq


COPY nginx_serv/ /sites/starter/          
COPY nginx_conf/ /etc/nginx/
COPY entrypoint-yandex-cert.sh /entrypoint-yandex-cert.sh



RUN if ! getent group www-data; then addgroup -S www-data; fi && \
    if ! getent passwd www-data; then adduser -S www-data -G www-data; fi


VOLUME ["/etc/letsencrypt", "/certbot/www", "/sites/starter"]


RUN chmod +x /entrypoint-yandex-cert.sh


ENTRYPOINT ["/entrypoint-yandex-cert.sh"]