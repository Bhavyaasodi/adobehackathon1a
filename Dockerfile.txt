# Use slim Python image
FROM python:3.10-slim

# Set working directory inside container
WORKDIR /app

# Copy app folder content into container
COPY ./app /app

# Copy requirements.txt
COPY requirements.txt .

# Install required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Create output directory (optional but safe)
RUN mkdir -p /app/output

# Run the main script when container starts
CMD ["python", "main.py"]
