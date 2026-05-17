FROM alpine:3.10.3

VOLUME /var/www/app/data
VOLUME /var/www/app/plugins
VOLUME /etc/nginx/ssl

EXPOSE 80 443

RUN apk --no-cache --update add \
    openssl unzip nginx bash ca-certificates s6 curl ssmtp mailx php7 php7-phar php7-curl \
    php7-fpm php7-json php7-zlib php7-xml php7-dom php7-ctype php7-opcache php7-zip php7-iconv \
    php7-pdo php7-pdo_mysql php7-pdo_sqlite php7-pdo_pgsql php7-mbstring php7-session php7-bcmath \
    php7-gd php7-mcrypt php7-openssl php7-sockets php7-posix php7-ldap php7-simplexml && \
    rm -rf /var/www/localhost && \
    rm -f /etc/php7/php-fpm.d/www.conf

COPY subjects/kanboard/ /var/www/app/
COPY subjects/kanboard/docker/ /

RUN rm -rf /var/www/app/docker && \
    find /usr/local/bin /etc/services.d -type f -exec sed -i 's/\r$//' {} \; && \
    chmod +x /usr/local/bin/entrypoint.sh /etc/services.d/*/run /etc/services.d/.s6-svscan/finish && \
    echo "rio-kanboard-v1.2.13" > /version.txt

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD []

