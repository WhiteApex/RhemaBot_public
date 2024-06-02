FROM python:3.12
COPY req.txt .
RUN pip install -r req.txt --no-cache-dir
WORKDIR /remabot
COPY config.py .
COPY db_worker.py .
COPY info.py .
COPY main.py .
CMD ["python3", "main.py"]
