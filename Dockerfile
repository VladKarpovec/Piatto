FROM python:3.11-slim-bullseye

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY .env /app/

COPY . /app/

RUN python manage.py collectstatic --noinput || true
RUN mkdir -p /app/media

VOLUME ["/app/media"]

EXPOSE 8004

ENTRYPOINT [ "gunicorn", "config.wsgi:application", "-b", "0.0.0.0:8004" ]
