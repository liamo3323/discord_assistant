# Use an official Python runtime as the base image
FROM python:3.11-slim

# Set the working directory to /app inside the container
WORKDIR /app

# Copy the requirements.txt file to the container
COPY requirements.txt .

# Install dependencies in a virtual environment
RUN python -m venv venv && \
    . venv/bin/activate && \
    pip install --no-cache-dir -r requirements.txt

# Copy the current directory (where app.py is) to the container
COPY . .

# Command to run the Python script
CMD ["venv/bin/python", "main.py"]