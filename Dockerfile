# FROM python:3.13-alpine

# WORKDIR /app

# COPY . .
# RUN pip install --no-cache-dir -r requirements.txt

# ENV PYTHONUNBUFFERED=1
# EXPOSE 5000

# CMD ["python", "app.py"]


# this is less troublesom than alpine
FROM python:3.13-slim AS builder

WORKDIR /app

COPY . .
RUN pip install --no-cache-dir --target=/app/deps -r requirements.txt


FROM gcr.io/distroless/python3
WORKDIR /app

COPY --from=builder /app /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/deps

EXPOSE 5000

CMD ["app.py"]
