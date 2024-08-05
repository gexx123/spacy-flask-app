# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    make \
    libatlas-base-dev \
    libffi-dev \
    curl

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Install pip
RUN pip install --upgrade pip

# Install required packages
RUN pip install -r requirements.txt

# Download the spaCy model and link it
RUN python -m spacy download en_core_web_sm && \
    python -m spacy link en_core_web_sm en

# Expose port 80
EXPOSE 80

# Run the application
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:80", "app:app"]