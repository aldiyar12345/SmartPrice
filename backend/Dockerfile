FROM python:3.10-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

COPY backend/ .

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
