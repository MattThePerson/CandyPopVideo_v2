FROM python:3.11-slim

# Install system deps
RUN apt-get update && apt-get install -y libgl1 ffmpeg && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install pip requirements in a local venv
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Expose port (change if needed)
EXPOSE 8013

# Run using uvicorn from the venv
CMD ["uvicorn", "python_src.main:app", "--host", "0.0.0.0", "--port", "8013"]
