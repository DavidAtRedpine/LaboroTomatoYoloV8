# Use an official Python image
FROM python:3.8-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git curl unzip vim libgl1-mesa-glx libglib2.0-0 \
    && apt-get clean

# Set the working directory
WORKDIR /app

# Clone the YOLO repository
RUN git clone https://github.com/autogyro/yolo-V8 /app/yolov8
WORKDIR /app/yolov8

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install requests ultralytics onnx onnxruntime

# Get tomato dataset and convert it to yolo format
COPY get_tomato_dataset.py /app/yolov8/get_tomato_dataset.py
RUN python /app/yolov8/get_tomato_dataset.py

# Yolo needs a "data.yaml" file to work
COPY data.yaml /app/yolov8/data.yaml
