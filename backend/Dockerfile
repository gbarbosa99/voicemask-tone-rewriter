# Base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install git and any other build tools
RUN apt-get update && \
    apt-get install -y git build-essential ffmpeg && \
    apt-get clean

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Run FastAPI app with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
