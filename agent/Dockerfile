FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8001
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]

# docker run -d --name redis -p 6379:6379 redis:7
# docker build -t agent:v1 .
# docker run -p 8001:8001 --link redis -e REDIS_PORT=6379 agent:v1