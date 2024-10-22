#!/bin/bash

# Function to handle cleanup on exit
cleanup() {
    echo "Cleaning up..."
    exit 0
}

# Trap SIGINT and SIGTERM signals
trap cleanup SIGINT SIGTERM


# Navigate to the bot directory
cd /home/discord-rasp/discord_assistant || { echo "Directory not found"; exit 1; }

# Pull the latest changes from the Git repository
echo "Pulling the latest changes from Git..."
git pull origin main  # Change 'main' to your branch name if different

# Build the Docker image
echo "Building the Docker image..."
sudo docker build -t discord-bot .

# Run the Docker container
echo "Running the Docker container..."
sudo docker run discord-bot  # Replace with your actual token or use an ENV variable

echo "Done!"