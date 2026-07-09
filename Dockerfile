# Python 3.12 + Django 5.1
FROM python:3.12-slim

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
