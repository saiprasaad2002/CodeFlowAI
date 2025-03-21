# Use the Python 3.11 slim image as the base image
FROM python:3.12-slim
 
# Set the working directory inside the container
# WORKDIR /lambda_function
 
# RUN mkdir /lambda_function/output_directory
 
# Copy Python files, requirements.txt, and all files/folders from the main directory into the container
COPY . .
# Install Python dependencies
RUN pip install -r requirements.txt
 
# RUN chmod -R 777 /
 
# Copy the .env file into the container (assuming it's in the same directory as the Dockerfile)
# COPY .env ./
 
# Expose port 8080
EXPOSE 8080
 
# Define environment variable
ENV NAME World
 
# Run the Python script with specified arguments when the container launches
CMD ["python", "app.py", "--port", "8080"]