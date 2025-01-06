# Use a specific version of the Python image to ensure consistency
FROM python:3.12-slim

# Install PostgreSQL development dependencies
RUN apt-get update && \
    apt-get install -y libpq-dev build-essential && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy only the requirements file first to cache dependencies
COPY requirements.txt /app/

# Install python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Now copy the rest of the application
COPY . /app/

# Expose port 5000 for the Flask app
EXPOSE 5000

# Set the environment variable for Flask
ENV FLASK_APP=app.py

# Run the Flask app when the container starts
CMD ["flask", "run", "--host=0.0.0.0"]
