# Use an official Python runtime as a parent image
FROM python:3.6-slim-jessie

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
ADD . /app

# Install any needed packages specified in requirements.txt
RUN pip install -i http://pypi.douban.com/simple/ --trusted-host pypi.douban.com -r requirements.txt

# Run app.py when the container launches
CMD ["python", "start_second_hands.py"]
