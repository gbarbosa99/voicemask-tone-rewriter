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

# Set PYTHONPATH so Melo can be found
ENV PYTHONPATH="/app/OpenVoice"

# Run the FastAPI server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
