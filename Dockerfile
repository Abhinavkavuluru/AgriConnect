# Use Python base image
FROM python:3.10

# Set working directory
WORKDIR /app

# Copy dependency files first
COPY requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy everything else
COPY . .

# Expose Flask port
EXPOSE 5000

# Run the app
CMD ["python", "app.py"]
