# Use an official Python runtime as a parent image
FROM python:3.12

# Copy the current directory contents into the container at /usr/src/app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Make port 8080 available to the world outside this container
EXPOSE 8080

# Define environment variable
ENV NAME World

ENTRYPOINT ["/entrypoint.sh"]