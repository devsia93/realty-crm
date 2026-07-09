# Python 3.9: Django 3.1 / psycopg2 2.8.6 ceiling; Phase 3 upgrades Django 5.x + Python 3.12
FROM python:3.9-slim

ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1

RUN groupadd -g 1000 app && useradd -m -u 1000 -g app app

WORKDIR /code
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ backend/
COPY frontend/ frontend/
RUN chown -R app:app /code
USER app

WORKDIR /code/backend
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
