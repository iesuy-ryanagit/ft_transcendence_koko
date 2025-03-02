#!/bin/sh

openssl genrsa -out /app/foobar.key 2048
openssl req -new -key /app/foobar.key -out /app/foobar.csr -subj "/C=US/ST=State/L=City/O=Organization/OU=Unit/CN=localhost"
openssl x509 -req -days 365 -in /app/foobar.csr -signkey /app/foobar.key -out /app/foobar.crt

python manage.py makemigrations --noinput
python manage.py migrate --noinput

python manage.py runsslserver 0.0.0.0:8000 --certificate foobar.crt --key foobar.key
