# Use the official Python base image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app
COPY requirements.txt /app
# Install the necessary dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Expose the port Flask will run on
EXPOSE 5000

# Set environment variable to indicate the app is in production mode
#ENV FLASK_APP=flask_for_startups.py
#ENV FLASK_RUN_HOST=0.0.0.0

# Run the Flask app in development mode
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
