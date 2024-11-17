# Use the official Python image from the Docker Hub
FROM python:3.12.3

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file
COPY req.txt .

# Install dependencies
RUN pip install -r req.txt

# Copy the rest of your application code
COPY . .

# Expose the port your app runs on
EXPOSE 8000

# Start the Django server and run migrations
CMD ["sh", "-c", "python manage.py makemigrations && python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
