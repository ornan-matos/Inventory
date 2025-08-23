#!/bin/sh

set -e

echo "Aplicando migrações do banco de dados..."
python manage.py migrate --noinput

echo "Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

python manage.py cleanup_old_records

exec "$@"
