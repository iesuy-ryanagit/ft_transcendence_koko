#!/bin/sh

python manage.py makemigrations --noinput
python manage.py migrate --noinput
python manage.py flush --noinput

exec "$@"
