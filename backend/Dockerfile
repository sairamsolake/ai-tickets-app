# Stage 1: Build and Lint
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# Enforce Ruff for linting in the pipeline
RUN ruff check . 

# Stage 2: Production Image
FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY main.py .

# Enforce secure non-root execution
RUN groupadd -r sairam && useradd -r -g sairam sairam
USER sairam

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
