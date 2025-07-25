FROM python:3.11-slim

# Install system deps
RUN apt-get update && apt-get install -y libgl1 ffmpeg

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install pip requirements in a local venv
RUN python -m venv .venv && \
    ./.venv/bin/pip install --upgrade pip && \
    ./.venv/bin/pip install -r requirements.txt

# Expose port (change if needed)
EXPOSE 8013

# Run using uvicorn from the venv
CMD ["./.venv/bin/uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8013"]
