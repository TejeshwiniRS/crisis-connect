FROM nvidia/cuda:12.2.2-runtime-ubuntu22.04
RUN apt-get update && apt-get install -y python3-pip ffmpeg && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY server.py .
ENV PORT=8080
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8080"]
