# Use an official Python image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app



# Copy only the requirements file
COPY requirements.txt /app/backend/

# Install dependencies
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Copy the rest of the backend code
COPY . /app/backend/




# Expose the FastAPI port
EXPOSE 80

# Command to run FastAPI
CMD ["uvicorn", "backend.main_api:app", "--host", "0.0.0.0", "--port", "80"]
