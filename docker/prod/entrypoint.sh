#!/usr/bin/env bash
set -e
cd /app

mkdir -p /app/staticfiles /app/media
python manage.py migrate --noinput
python manage.py collectstatic --noinput

# створити суперкористувача, якщо його ще немає
python - <<'PY'
import os, django
from django.contrib.auth import get_user_model
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()
User = get_user_model()
u = os.getenv("DJANGO_SUPERUSER_USERNAME")
e = os.getenv("DJANGO_SUPERUSER_EMAIL")
p = os.getenv("DJANGO_SUPERUSER_PASSWORD")
if u and p and not User.objects.filter(username=u).exists():
    User.objects.create_superuser(username=u, email=e or "", password=p)
    print(f"[INIT] Superuser '{u}' created")
else:
    print("[INIT] Superuser exists or env not set")
PY


if [ -n "${DATABASE_URL}" ]; then WORKERS="${GUNICORN_WORKERS:-2}"; else WORKERS="${GUNICORN_WORKERS:-1}"; fi
THREADS="${GUNICORN_THREADS:-1}"
TIMEOUT="${GUNICORN_TIMEOUT:-120}"

exec gunicorn config.wsgi:application \
  -b 0.0.0.0:"${PORT:-8000}" \
  --workers "${WORKERS}" \
  --threads "${THREADS}" \
  --timeout "${TIMEOUT}"
