FROM python:3.11-slim

COPY . /app
WORKDIR /app

ENV TEMP /tmp
RUN mkdir -p $TEMP

RUN apt-get update && apt-get install -y \
    ffmpeg \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "run.py"]
