# Python image
FROM python:3.9-slim

# Setting a work dir
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application
COPY ./app ./app
COPY ./run.py ./run.py

# Run Flask application devlopment 
# CMD ["flask", "run", "--host=0.0.0.0"]

# Run Flask application production
CMD ["gunicorn", "run:app", "--bind", "0.0.0.0:5000", "--workers", "2"]
