# Filename: Dockerfile
FROM python:3.11-slim-bookworm

# Copy in our requirements install
WORKDIR /app/
COPY requirements.txt ./
RUN python3 -m pip install -r ./requirements.txt

# Copy Source code
COPY . .