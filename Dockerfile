### build stage
FROM python:3.13-alpine AS builder

WORKDIR /app

COPY ./requirements.txt .

# Install dependencies into a virtual environment
RUN python -m venv venv && \
    . venv/bin/activate && \
    python -m pip install -r requirements.txt

### runtime stage
FROM python:3.13-alpine AS production

COPY --from=builder /app/venv /app/venv

WORKDIR /app

COPY . .

# RUN useradd --create-home appuser
# USER appuser

# Set environment variables to use the virtual environment
ENV PATH="/app/venv/bin:$PATH"

EXPOSE 5000

CMD ["python", "app.py"]