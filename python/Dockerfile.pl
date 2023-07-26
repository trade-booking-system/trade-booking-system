FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY listeners/requirements.txt .
RUN python -m pip install -r requirements.txt

WORKDIR /app
COPY ./listeners/pl_listener.py /app/listeners/
COPY ./listeners/listener.py /app/listeners/
COPY schema /app/schema
COPY utils /app/utils

RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

ENV PYTHONPATH /app
CMD ["python", "listeners/pl_listener.py"]
