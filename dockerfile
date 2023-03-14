# syntax=docker/dockerfile:1
FROM python:3.11-slim-bullseye

# Create working directory of '/app' under root
WORKDIR /app
COPY app /app

# Install requirements for slim-bullseye
RUN apt-get update && apt-get install -y --no-install-recommends build-essential git gcc make cmake && rm -rf /var/lib/apt/lists/*
RUN git clone https://github.com/WebBreacher/WhatsMyName /app/WhatsMyName
RUN pip3 install -r requirements.txt

ENTRYPOINT ["python3", "main.py"]
CMD ["-a", ""]