# Use official Python image
FROM python:3

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy all files
COPY . /app/

# Expose port 8000
EXPOSE 8001

# Run server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8001"]