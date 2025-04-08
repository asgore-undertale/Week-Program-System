FROM python:3.13-alpine

WORKDIR /app

# 1 layer: install runtime deps (no venv)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 1 layer: copy your app
COPY . .

# metadata/env is just one layer
ENV PYTHONUNBUFFERED=1

EXPOSE 5000

# final layer: default command
CMD ["python", "app.py"]
