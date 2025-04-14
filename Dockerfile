FROM python:3.13-slim AS builder

WORKDIR /app

COPY . .
RUN pip install --no-cache-dir --target=/app/deps -r requirements.txt


FROM gcr.io/distroless/python3:nonroot
WORKDIR /app

COPY --from=builder /app /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/deps

EXPOSE 5000

CMD ["app.py"]
