# Use a lightweight, stable version of Python as the base image
FROM python:3.11-slim

# Set environment variables to prevent Python from writing .pyc files and ensure output is visible immediately
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies needed for PostgreSQL (psycopg2) and building Python packages
# 'build-essential' is required for compiling some Python packages
RUN apt-get update \
    && apt-get install -y postgresql-client build-essential git \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file and install Python dependencies
# This is done separately to leverage Docker's build cache (if requirements.txt doesn't change, this step is skipped)
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the rest of the application code into the container
COPY . /app/

# Expose the port Gunicorn will listen on (Django's default)
EXPOSE 8000

# Define the command to run your application using Gunicorn
# Gunicorn listens on 0.0.0.0:8000
# IMPORTANT: Replace 'rug_api.wsgi:application' with the actual path to your project's WSGI file if your top-level project folder is named differently.
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "api.wsgi:application"]
