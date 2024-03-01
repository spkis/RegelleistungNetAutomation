# Use the official Python image as the base image
FROM python:3.12.2

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application's code
COPY regelleistung_fcr_results.py .

# Command to run on container start
CMD [ "python", "./regelleistung_fcr_results.py" ]