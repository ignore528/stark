# ---- Base image (Python 3.13 slim) ----
FROM python:3.13-slim

# ---- Set working directory ----
WORKDIR /app

# ---- Copy all project files ----
COPY . /app

# ---- Install system dependencies ----
RUN apt-get update && apt-get install -y \
    git curl ffmpeg build-essential \
    && curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs \
    && echo "Node: $(node -v) | npm: $(npm -v)" \
    && pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt \
    && rm -rf /var/lib/apt/lists/*

# ---- Default command ----
CMD ["python", "run.py"]
