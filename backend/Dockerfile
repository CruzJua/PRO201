FROM python:3.11-slim

# Build context is the repository root so the sibling `database` package can be
# copied in alongside the backend. Paths mirror the repo layout, which is what
# main.py's `get_db()` expects when it adds the parent directory to sys.path.
WORKDIR /app/backend

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .
COPY database/ /app/database/

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
