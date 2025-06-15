FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git ffmpeg libsndfile1 curl && \
    apt-get clean

# Set working directory
WORKDIR /app

# Copy all backend files
COPY . .

# Install Python packages
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install git+https://github.com/myshell-ai/MeloTTS.git && \
    python -m unidic download

ENV PYTHONPATH="/app"

# Download model weights from GitHub release
RUN mkdir -p backend/Openvoice/checkpoints/base_speakers/EN \
 && mkdir -p backend/Openvoice/checkpoints/converter \
 && curl -L -o backend/Openvoice/checkpoints/base_speakers/EN/checkpoint.pth https://github.com/gbarbosa99/voicemask-tone-rewriter/releases/download/v1.0.0/base_speakers_EN_checkpoint.pth \
 && curl -L -o backend/Openvoice/checkpoints/base_speakers/EN/config.json https://github.com/gbarbosa99/voicemask-tone-rewriter/releases/download/v1.0.0/base_speakers_EN_config.json \
 && curl -L -o backend/Openvoice/checkpoints/base_speakers/EN/en_default_se.pth https://github.com/gbarbosa99/voicemask-tone-rewriter/releases/download/v1.0.0/base_speakers_EN_en_default_se.pth \
 && curl -L -o backend/Openvoice/checkpoints/base_speakers/EN/en_style_se.pth https://github.com/gbarbosa99/voicemask-tone-rewriter/releases/download/v1.0.0/base_speakers_EN_en_style_se.pth \
 && curl -L -o backend/Openvoice/checkpoints/converter/checkpoint.pth https://github.com/gbarbosa99/voicemask-tone-rewriter/releases/download/v1.0.0/converter_checkpoint.pth \
 && curl -L -o backend/Openvoice/checkpoints/converter/config.json https://github.com/gbarbosa99/voicemask-tone-rewriter/releases/download/v1.0.0/converter_config.json

# Run the FastAPI server
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
