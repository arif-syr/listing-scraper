FROM python:3.12-slim-bookworm
LABEL authors="arif"

WORKDIR /usr/src/app

COPY requirements.txt ./

# Install micro as a text editor and clean it up afterwards to keep the image size down
# Replace micro with your preferred editor
RUN apt-get update && \
   apt-get install -y micro && \
   rm -rf /var/lib/apt/lists/*

# Install required packages
RUN pip install -r requirements.txt

COPY . .
