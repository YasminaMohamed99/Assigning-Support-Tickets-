# Step 1: Use the official Python 3.12 image as the base
FROM python:3.12-slim

# Step 2: Set environment variables to improve Python performance
ENV PYTHONDONTWRITEBYTECODE 1  # Prevents Python from writing pyc files to disk
ENV PYTHONUNBUFFERED 1  # Ensures that Python outputs are immediately available, no buffering

# Step 3: Set the working directory to /app
WORKDIR /app

# Step 4: Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && apt-get clean  # Install build tools and PostgreSQL libraries

# Step 5: Install Python dependencies from the requirements file
#Copy the requirements file into the container
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Step 6: Copy your entire project into the container
# Copy the Django project files into the container
COPY . /app/

# Step 7: Expose port 8000 for the Django app to be accessible from outside
EXPOSE 8000

# Step 8: Use Gunicorn to serve the Django app (production WSGI server)
CMD ["gunicorn", "support_system.wsgi:application", "--bind", "0.0.0.0:8000"]