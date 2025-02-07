FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first to leverage Docker cache
COPY backend/requirements.txt .

# Install dependencies in smaller chunks to avoid memory issues
RUN pip install --no-cache-dir --disable-pip-version-check \
    fastapi==0.104.1 \
    uvicorn==0.24.0 \
    python-multipart==0.0.6 \
    ffmpeg-python==0.2.0 \
    python-dotenv==1.0.0 \
    celery[redis]==5.3.6 \
    redis==5.0.1 \
    boto3==1.29.3 \
    pydantic>=2.0.0 \
    sqlalchemy==2.0.23 \
    psycopg2-binary==2.9.9 \
    python-jose[cryptography]==3.3.0 \
    passlib[bcrypt]==1.7.4 \
    google-generativeai>=0.3.0 \
    moviepy==1.0.3

# Install ML dependencies separately
RUN pip install --no-cache-dir --disable-pip-version-check \
    torch==2.6.0 \
    torchaudio==2.6.0 \
    numpy>=1.24.0 \
    transformers>=4.30.0 \
    git+https://github.com/openai/whisper.git

# Install audio processing dependencies
RUN pip install --no-cache-dir --disable-pip-version-check \
    soundfile>=0.12.1 \
    librosa>=0.10.0 \
    scipy>=1.11.0 \
    gTTS==2.3.2

# Copy the rest of the application
COPY backend .

# Expose the port
EXPOSE 8000

# Command to run the application
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"] 