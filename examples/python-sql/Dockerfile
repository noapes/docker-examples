# Use an official Python runtime as a parent image
FROM python:3.6.6-slim

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
ADD . /app

# Install and need packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt -v

# create a directory for qrcode
RUN mkdir /mnt/qrcode

# Define environment variable
# ENV PATH ~/qrcode

# Make port 80 available to the world outside this container
EXPOSE 80

# RUN app.py when the container launches
CMD ["python","handle_qrcode.py"]
