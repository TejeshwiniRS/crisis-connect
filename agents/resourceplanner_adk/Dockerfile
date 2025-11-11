# ----------------------------------------
# Dockerfile for resourceplanner_adk agent
# ----------------------------------------
FROM python:3.12-slim

# Prevent Python from writing .pyc files and buffering stdout
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the agent source
COPY . .

# Expose port for Cloud Run
EXPOSE 8080

# Let Cloud Run tell the app which port to use
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]
