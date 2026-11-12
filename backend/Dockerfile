# Base python 3.11 image (Debian Bookworm)
FROM python:3.11-slim-bookworm

# Avoid prompts from debconf
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install system dependencies:
# - ffmpeg (latest from bookworm repository)
# - fonts for video subtitles burn-in
# - libgl1, libglib2.0-0 for opencv
# - curl, git for utilities
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    fonts-freefont-ttf \
    fonts-dejavu-core \
    fontconfig \
    libgl1 \
    libglib2.0-0 \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Verify ffmpeg and fontconfig
RUN ffmpeg -version && fc-cache -f -v

# Set working directory
WORKDIR /app

# Copy dependency requirements
COPY requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Create necessary working directories
RUN mkdir -p /app/outputs /app/temp /app/assets/broll

# Copy source code
COPY . .

# Expose standard port
EXPOSE 8000

# Start FastAPI server via Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

