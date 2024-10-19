#!/bin/bash

# Change to the project directory
cd ~/discord_assistant || exit 1  # Change this to your project directory

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