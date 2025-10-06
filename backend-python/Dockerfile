# Base com libs geoespaciais necessárias
FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive     PYTHONDONTWRITEBYTECODE=1     PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gdal-bin libgdal-dev libpq-dev proj-bin libproj-dev \
    libgeos-dev libspatialindex-dev curl ca-certificates && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

ENV PYTHONPATH=/app

EXPOSE 8000
