# Use Ubuntu as base image for better WSL compatibility
FROM ubuntu:22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies and Python
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Create symlinks for python
RUN ln -s /usr/bin/python3 /usr/bin/python

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ src/

# Fix permissions for WSL compatibility
RUN mkdir -p /tmp/wsltmp && chmod 777 /tmp/wsltmp
ENV TMPDIR=/tmp/wsltmp

# Create non-root user but with necessary permissions
RUN useradd -m appuser && chown -R appuser:appuser /app /tmp/wsltmp
USER appuser

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["python", "src/bot.py"]