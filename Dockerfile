FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements-2.txt .

RUN pip install \
    --no-cache-dir \
    --default-timeout=180 \
    --retries=5 \
    -r requirements-2.txt

COPY app ./app
COPY alembic.ini .
COPY alembic ./alembic
COPY ml ./ml

EXPOSE 8000

# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]