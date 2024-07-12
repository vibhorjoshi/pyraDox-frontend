FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies

# Copy the current directory contents into the container at /app

# Build Python APP Here
RUN mkdir aadhaar_ocr_masking

COPY app.py /aadhaar_ocr_masking/app.py
COPY pyradox.py /aadhaar_ocr_masking/pyradox.py

# Install any needed packages specified in requirements.txt
# (You'll need to create this file with the necessary dependencies)
COPY requirements.txt /aadhaar_ocr_masking/requirements.txt

RUN cd aadhaar_ocr_masking && \
    pip install -r requirements.txt

# Make port 9001 available to the world outside this container

# Run app.py when the container launches
CMD ["streamlit", "run", "pyradox.py", "app.py"]