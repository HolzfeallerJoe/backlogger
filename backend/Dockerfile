FROM python:3.9.23

WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend .
COPY ../frontend ./frontend
COPY ../static ./static

CMD ["fastapi", "run", "./main.py"]
