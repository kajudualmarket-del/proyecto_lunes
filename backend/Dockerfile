# backend/Dockerfile
FROM python:3.11-bullseye

WORKDIR /app

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements y instalar Python packages
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir cryptography python-multipart
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la app
COPY ./app ./app

# Comando de inicio
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8009"]
