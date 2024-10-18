# Use an official Python runtime as the base image
FROM python:3.9-slim

# Set the working directory to /app inside the container
WORKDIR /app

# Copy the current directory (where app.py is) to the container
COPY . .

# Install any necessary dependencies
RUN pip install -r requirements.txt

# Command to run the Python script
CMD ["python", "main.py"]