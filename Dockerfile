# Use an official Python 3.12 image from DockerHub
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install required Python packages
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Set environment variables if needed
ENV GOOGLE_CREDENTIALS="<your_json_content_here>"
ENV TELEGRAM_TOKEN="<your_telegram_token_here>"

# Run the application
CMD ["python", "main.py"]