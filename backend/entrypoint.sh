#!/bin/sh
set -e

python - <<'PY'
import os
import time
import psycopg2

host = os.getenv("DB_HOST", "db")
port = int(os.getenv("DB_PORT", "5432"))
dbname = os.getenv("POSTGRES_DB", "")
user = os.getenv("POSTGRES_USER", "")
password = os.getenv("POSTGRES_PASSWORD", "")

for _ in range(30):
    try:
        psycopg2.connect(
            host=host,
            port=port,
            dbname=dbname,
            user=user,
            password=password,
        ).close()
        break
    except Exception:
        time.sleep(2)
else:
    raise SystemExit("Database is unavailable")
PY

python manage.py migrate --noinput
python manage.py collectstatic --noinput
if [ -f /data/ingredients.csv ]; then
  python manage.py load_ingredients --path /data/ingredients.csv
fi

WORKERS="${GUNICORN_WORKERS:-3}"
TIMEOUT="${GUNICORN_TIMEOUT:-120}"

exec gunicorn foodgram.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers "${WORKERS}" \
  --timeout "${TIMEOUT}" \
  --access-logfile - \
  --error-logfile -
