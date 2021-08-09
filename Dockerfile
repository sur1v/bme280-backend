FROM python:3.8-alpine

# Docs
LABEL maintainer="https://github.com/sur1v"
EXPOSE 8000/tcp

# App
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt

# Just one worker
CMD ["gunicorn", "-b", "0.0.0.0:8000", "-w", "1", "bme280-backend:app"]
