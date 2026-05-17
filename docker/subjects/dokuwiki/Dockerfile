FROM php:5.6-apache

RUN a2enmod rewrite

WORKDIR /var/www/html

COPY subjects/dokuwiki/ /var/www/html/

RUN chown -R www-data:www-data /var/www/html/data /var/www/html/conf || true

EXPOSE 80

