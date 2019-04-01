# Use an official Python runtime as a parent image
FROM python:3.5.5-slim-jessie

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
ADD . /app

# Install any needed packages specified in requirements.txt
RUN pip install -i http://pypi.douban.com/simple/ --trusted-host pypi.douban.com -r requirements.txt

# Run run.py when the container launches
CMD ["python", "start_script.py"]