#!/bin/sh

echo "Aguardando o PostgreSQL iniciar..."

while ! nc -z db 5432; do
  sleep 1
done

echo "PostgreSQL iniciado com sucesso."

echo "Aplicando as migrações do banco de dados..."
python manage.py migrate

exec "$@"