# docker build -t cpop-vids .
# 
# docker run \
# -v "/mnt/a/Whispera/videos:/app/videos" \
# -v "/mnt/a/WhisperaHQ/.AppData/CandyPopVideo:/app/appdata" \
# -v "${PWD}/config.yaml:/app/config.yaml" \
# -p 8013:8013 --name CandyPopVideo cpop-vids

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install python deps (before full copy for caching)
COPY requirements.txt .
RUN pip install uv && \
    uv pip install --system -r requirements.txt

# Copy project files
COPY . .

# Install system deps
RUN apt-get update && \
    apt-get install -y wget libgl1 ffmpeg && \
    apt-get install -y wget && \
    wget https://go.dev/dl/go1.24.0.linux-amd64.tar.gz && \
    tar -C /usr/local -xzf go1.24.0.linux-amd64.tar.gz && \
    ln -s /usr/local/go/bin/go /usr/bin/go && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Build Go executable
RUN go mod tidy -C go_backend && \
    go build -C go_backend -ldflags="-s -w" -o ../CandyPopVideo

# Expose port (change if needed)
EXPOSE 8013

# Run using uvicorn from the venv
CMD ["./CandyPopVideo", "--port", "8013"]
