version: "3.9"

services:
  web:
    build:
      context: .
      dockerfile: docker/local/Dockerfile
    env_file:
      - .env
    ports:
      - "8000:8000"
    volumes:
      - .:/app
      - media:/app/media
    restart: unless-stopped

volumes:
  media: