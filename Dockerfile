FROM python:3.9

# Set the working directory
WORKDIR /app

# Copy only the requirements.txt file first
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY . /app

# Install Redis server
RUN apt-get update \
    && apt-get install -y redis-server

# Expose the Flask app port
EXPOSE 5000

# Start Redis server and run the Python application
CMD ["bash", "-c", "service redis-server start && python run.py"]
