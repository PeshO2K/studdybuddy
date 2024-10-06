# wait-for-postgres.sh
#!/bin/sh
until nc -z postgres 5432; do
  echo "Waiting for PostgreSQL..."
  sleep 1
done
exec "$@"
