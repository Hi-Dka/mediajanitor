FROM python:3.12-slim

ENV MEDIAJANITOR_VERSION=1.0.0
ENV PYTHONPATH=/app

WORKDIR /app

COPY /app/ .
COPY requirements.txt .
COPY entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r /app/requirements.txt

ENTRYPOINT ["/entrypoint.sh"]
