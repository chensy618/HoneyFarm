FROM python:3.13-alpine

COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["python3", "./server.py", "--bind", "0.0.0.0", "--log-file", "log/miniprint.json"]
