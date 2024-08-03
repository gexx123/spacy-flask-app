# Use an official Python runtime as a parent image
FROM python:3.11

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Install any needed packages specified in requirements.txt
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Download the spaCy model
RUN python -m spacy download en_core_web_sm

# Make port 80 available to the world outside this container
EXPOSE 80

# Run app.py when the container launches
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:80", "app:app"]
