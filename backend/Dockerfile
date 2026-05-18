FROM python:3.11-slim AS builder

WORKDIR /build
COPY pyproject.toml .
COPY verity/ verity/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

FROM python:3.11-slim

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY verity/ verity/

# Chroma index is downloaded from S3 at startup if not present
ENV CHROMA_DIR=/app/data/chroma
ENV PORT=8000

EXPOSE 8000

CMD ["uvicorn", "verity.api:app", "--host", "0.0.0.0", "--port", "8000"]
