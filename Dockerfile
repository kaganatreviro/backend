FROM python:3.11-slim as builder

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


WORKDIR /code

RUN apt-get update \
    && apt-get install -y \
        binutils \
        gcc \
        gdal-bin \
        libpq-dev \
        libproj-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade pip \
    && pip install -r requirements.txt

COPY . .


CMD ["uvicorn", "happyhours.asgi:application", "--host", "0.0.0.0", "--port", "8000"]
