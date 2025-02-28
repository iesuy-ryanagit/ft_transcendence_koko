#!/bin/sh

python manage.py makemigrations --noinput
python manage.py migrate --noinput

exec "$@"

gunicorn --bind 0.0.0.0:8000 account.wsgi:application
