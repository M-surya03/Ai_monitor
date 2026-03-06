# Base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy dependency file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose Flask port
EXPOSE 5001

# Environment variables
ENV PYTHONUNBUFFERED=1

# Start the API
CMD ["python", "llm_api.py"]