FROM python:3.11-slim

COPY . /app
WORKDIR /app

ENV TEMP /tmp
RUN mkdir -p $TEMP

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "run.py"]